# Here are the views for interacting with the archive Model
# exclusively.

import logging
import re
from os.path import basename
from urllib.parse import quote, urlparse, unquote
import typing
from typing import Optional
import base64

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, InvalidPage, EmptyPage, Page
from django.urls import reverse
from django.db import transaction
from django.http import Http404, HttpRequest
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.conf import settings

from core.base.setup import Settings
from core.local.foldercrawlerthread import FolderCrawlerThread
from viewer.utils.actions import event_log
from viewer.forms import (
    ArchiveModForm, ImageFormSet,
    ArchiveEditForm, ArchiveManageEditFormSet)
from viewer.models import (
    Archive, Tag, Gallery, Image,
    UserArchivePrefs, ArchiveManageEntry
)
from viewer.views.head import render_error

logger = logging.getLogger(__name__)
crawler_settings = settings.CRAWLER_SETTINGS


archive_download_regex = re.compile(r"/archive/(\d+)/download/$", re.IGNORECASE)


def archive_details(request: HttpRequest, pk: int, view: str = "cover") -> HttpResponse:
    """Archive listing."""

    try:
        archive = Archive.objects.get(pk=pk)
    except Archive.DoesNotExist:
        raise Http404("Archive does not exist")
    if not archive.public and not request.user.is_authenticated:
        raise Http404("Archive does not exist")

    if not request.user.is_authenticated:
        view = "cover"

    d: dict[str, typing.Any] = {'archive': archive, 'view': view}

    num_images = 30
    if view in ("full", "edit"):
        num_images = 10
    if view in ("single", "cover"):
        num_images = 1

    if request.user.is_authenticated:

        images = archive.image_set.filter(extracted=True)

        if images:
            paginator = Paginator(images, num_images)
            try:
                page = int(request.GET.get("page", '1'))
            except ValueError:
                page = 1

            try:
                images_page: typing.Optional[Page] = paginator.page(page)
            except (InvalidPage, EmptyPage):
                images_page = paginator.page(paginator.num_pages)

        else:
            images_page = None

        d.update({'images': images_page})

    if view == "edit" and request.user.is_staff:

        paginator = Paginator(archive.image_set.all(), num_images)
        try:
            page = int(request.GET.get("page", '1'))
        except ValueError:
            page = 1

        try:
            all_images = paginator.page(page)
        except (InvalidPage, EmptyPage):
            all_images = paginator.page(paginator.num_pages)

        form = ArchiveModForm(instance=archive)
        image_formset = ImageFormSet(
            queryset=all_images.object_list,
            prefix='images'
        )
        d.update({
            'form': form,
            'image_formset': image_formset,
            'matchers': crawler_settings.provider_context.get_matchers(crawler_settings, force=True),
            'api_key': crawler_settings.api_key,
        })

    if request.user.is_authenticated:
        current_user_archive_preferences, created = UserArchivePrefs.objects.get_or_create(
            user__id=request.user.pk,
            archive=archive,
            defaults={'user_id': request.user.pk, 'archive': archive, 'favorite_group': 0}
        )
        d.update({'user_archive_preferences': current_user_archive_preferences})

    # In-place collaborator edit form
    if request.user.has_perm('viewer.change_archive'):
        if request.POST.get('change-archive'):
            # create a form instance and populate it with data from the request:
            old_gallery = archive.gallery
            edit_form = ArchiveEditForm(request.POST, instance=archive)
            # check whether it's valid:
            if edit_form.is_valid():
                # TODO: Maybe this should be in save method for the form
                new_archive = edit_form.save(commit=False)
                new_archive.simple_save()
                edit_form.save_m2m()
                if new_archive.gallery:
                    if new_archive.gallery.tags.all():
                        new_archive.tags.set(new_archive.gallery.tags.all())
                    if new_archive.gallery != old_gallery:
                        new_archive.title = new_archive.gallery.title
                        new_archive.title_jpn = new_archive.gallery.title_jpn
                        if edit_form.cleaned_data['old_gallery_to_alt'] and old_gallery is not None:
                            new_archive.alternative_sources.add(old_gallery)
                        new_archive.simple_save()
                        edit_form = ArchiveEditForm(instance=new_archive)

                message = 'Archive successfully modified'
                messages.success(request, message)
                logger.info("User {}: {}".format(request.user.username, message))
                event_log(
                    request.user,
                    'CHANGE_ARCHIVE',
                    content_object=new_archive,
                    result='changed'
                )
                # return HttpResponseRedirect(request.META["HTTP_REFERER"])
            else:
                messages.error(request, 'The provided data is not valid', extra_tags='danger')
                # return HttpResponseRedirect(request.META["HTTP_REFERER"])
        else:
            edit_form = ArchiveEditForm(instance=archive)
        d.update({'edit_form': edit_form})

    if request.user.has_perm('viewer.mark_archive') and request.user.is_authenticated:
        if request.POST.get('manage-archive'):
            archive_manage_formset = ArchiveManageEditFormSet(request.POST, instance=archive)
            # check whether it's valid:
            if archive_manage_formset.is_valid():

                archive_manages = archive_manage_formset.save(commit=False)
                for manage_instance in archive_manages:
                    if manage_instance.pk is None:
                        manage_instance.archive = archive
                        manage_instance.mark_check = True
                        manage_instance.mark_user = request.user
                        manage_instance.origin = ArchiveManageEntry.ORIGIN_USER
                        event_log(
                            request.user,
                            'MARK_ARCHIVE',
                            content_object=archive,
                            result='created'
                        )
                    else:
                        event_log(
                            request.user,
                            'MARK_ARCHIVE',
                            content_object=archive,
                            result='modified'
                        )
                    manage_instance.save()
                for manage_instance in archive_manage_formset.deleted_objects:
                    if manage_instance.mark_user != request.user and not request.user.is_staff:
                        messages.error(request, 'Cannot delete the specified mark, you are not the owner', extra_tags='danger')
                    else:
                        event_log(
                            request.user,
                            'MARK_ARCHIVE',
                            content_object=archive,
                            result='deleted'
                        )
                        manage_instance.delete()

                messages.success(request, 'Sucessfully modified Archive manage data')
                archive_manage_formset = ArchiveManageEditFormSet(instance=archive, queryset=ArchiveManageEntry.objects.filter(mark_user=request.user))
            else:
                messages.error(request, 'The provided data is not valid', extra_tags='danger')
        else:
            archive_manage_formset = ArchiveManageEditFormSet(instance=archive, queryset=ArchiveManageEntry.objects.filter(mark_user=request.user))

        d.update({'archive_manage_formset': archive_manage_formset})

    if request.user.has_perm('viewer.view_marks'):
        manage_entries = ArchiveManageEntry.objects.filter(archive=archive)
        d.update({'manage_entries': manage_entries, 'manage_entries_count': manage_entries.count()})

    d.update({'tag_count': archive.tags.all().count(), 'custom_tag_count': archive.custom_tags.all().count()})

    return render(request, "viewer/archive.html", d)


@login_required
def archive_update(request: HttpRequest, pk: int, tool: str = None, tool_use_id: str = None) -> HttpResponse:
    """Update archive title, rating, tags, archives."""
    if not request.user.is_staff:
        messages.error(request, "You need to be an admin to update an archive.")
        return HttpResponseRedirect(request.META["HTTP_REFERER"])
    try:
        archive = Archive.objects.get(pk=pk)
    except Archive.DoesNotExist:
        raise Http404("Archive does not exist")

    if tool == 'select-as-match' and tool_use_id:
        try:
            gallery_id = int(tool_use_id)
            archive.select_as_match(gallery_id)
            if archive.gallery:
                logger.info("Archive {} ({}) was matched with gallery {} ({}).".format(
                    archive,
                    reverse('viewer:archive', args=(archive.pk,)),
                    archive.gallery,
                    reverse('viewer:gallery', args=(archive.gallery.pk,)),
                ))
        except ValueError:
            return HttpResponseRedirect(request.META["HTTP_REFERER"])
        return HttpResponseRedirect(request.META["HTTP_REFERER"])
    elif tool == 'clear-possible-matches':
        archive.possible_matches.clear()
        return HttpResponseRedirect(request.META["HTTP_REFERER"])

    current_user_archive_preferences, created = UserArchivePrefs.objects.get_or_create(
        user__id=request.user.pk,
        archive=archive,
        defaults={'user_id': request.user.pk, 'archive': archive, 'favorite_group': 0}
    )

    d = {'archive': archive, 'view': "edit", 'user_archive_preferences': current_user_archive_preferences}

    if request.method == 'POST':
        p = request.POST
        image_formset = ImageFormSet(p,
                                     queryset=archive.image_set.all(),
                                     prefix='images')
        if image_formset.is_valid():
            images = image_formset.save(commit=False)
            for image in images:
                image.save()
            for image in image_formset.deleted_objects:
                image.delete_plus_files()

            # Force relative positions
            for count, image in enumerate(archive.image_set.all(), start=1):
                image.position = count
                # image.archive_position = count
                image.save()

        archive.title = p["title"]
        archive.title_jpn = p["title_jpn"]
        archive.source_type = p["source_type"]
        archive.reason = p["reason"]
        archive.details = p["details"]

        if "zipped" in p:
            if p["zipped"] != '' and p["zipped"] != archive.zipped:
                result = archive.rename_zipped_pathname(p["zipped"])
                if not result:
                    messages.error(request, "File {} already exists, renaming failed".format(p["zipped"]))

        if "custom_tags" in p:
            lst = []
            tags = p.getlist("custom_tags")
            for t in tags:
                lst.append(Tag.objects.get(pk=t))
            archive.custom_tags.set(lst)
        else:
            archive.custom_tags.clear()
        if "possible_matches" in p and p["possible_matches"] != "":

            matched_gallery = Gallery.objects.get(pk=p["possible_matches"])

            archive.gallery_id = p["possible_matches"]
            archive.title = matched_gallery.title
            archive.title_jpn = matched_gallery.title_jpn
            archive.tags.set(matched_gallery.tags.all())

            archive.match_type = "manual:cutoff"
            archive.possible_matches.clear()

            if 'failed' in matched_gallery.dl_type:
                matched_gallery.dl_type = 'manual:matched'
                matched_gallery.save()
        if "alternative_sources" in p:
            lst = []
            alternative_sources = p.getlist("alternative_sources")
            for alternative_gallery in alternative_sources:
                lst.append(Gallery.objects.get(pk=alternative_gallery))
            archive.alternative_sources.set(lst)
        else:
            archive.alternative_sources.clear()
        archive.simple_save()

        messages.success(request, 'Updated archive: {}'.format(archive.title))

    else:
        image_formset = ImageFormSet(
            queryset=archive.image_set.all(),
            prefix='images'
        )
    form = ArchiveModForm(instance=archive)
    d.update({
        'form': form,
        'image_formset': image_formset,
        'matchers': crawler_settings.provider_context.get_matchers(crawler_settings, force=True),
        'api_key': crawler_settings.api_key,
    })

    return HttpResponseRedirect(request.META["HTTP_REFERER"])


def archive_auth(request: HttpRequest) -> HttpResponse:
    archive_url = request.META.get('HTTP_X_ORIGINAL_URI', None)
    if archive_url is None:
        return HttpResponse(status=403)

    archive_parts = urlparse(archive_url)

    archive_path = unquote(archive_parts.path).removeprefix('/download/')
    try:
        archive = Archive.objects.get(zipped=archive_path)
    except Archive.DoesNotExist:
        return HttpResponse(status=403)
    if not archive.public and not request.user.is_authenticated:
        return HttpResponse(status=403)
    return HttpResponse(status=200)


def archive_download(request: HttpRequest, pk: int) -> HttpResponse:
    try:
        archive = Archive.objects.get(pk=pk)
    except Archive.DoesNotExist:
        raise Http404("Archive does not exist")
    if not archive.public and not request.user.is_authenticated:
        raise Http404("Archive does not exist")
    if 'HTTP_X_FORWARDED_HOST' in request.META:
        response = HttpResponse()
        response["Content-Type"] = "application/zip"
        if 'original' in request.GET:
            response["Content-Disposition"] = 'attachment; filename*=UTF-8\'\'{0}'.format(
                quote(basename(archive.zipped.name)))
        else:
            response["Content-Disposition"] = 'attachment; filename*=UTF-8\'\'{0}'.format(
                archive.pretty_name)
        response['X-Accel-Redirect'] = "/download/{0}".format(quote(archive.zipped.name)).encode('utf-8')
        return response
    else:
        return HttpResponseRedirect(archive.zipped.url)


def archive_ext_download(request: HttpRequest, pk: int) -> HttpResponse:
    try:
        archive = Archive.objects.get(pk=pk)
    except Archive.DoesNotExist:
        raise Http404("Archive does not exist")
    if not archive.public and not request.user.is_authenticated:
        raise Http404("Archive does not exist")

    if 'original' in request.GET:
        filename = quote(basename(archive.zipped.name))
    else:
        filename = archive.pretty_name

    redirect_url = "{0}/{1}?filename={2}".format(
        crawler_settings.urls.external_media_server,
        quote(archive.zipped.name),
        filename
    )

    return HttpResponseRedirect(redirect_url)


def archive_thumb(request: HttpRequest, pk: int) -> HttpResponse:
    try:
        archive = Archive.objects.get(pk=pk)
    except Archive.DoesNotExist:
        raise Http404("Archive does not exist")
    if not archive.public and not request.user.is_authenticated:
        raise Http404("Archive does not exist")
    if 'HTTP_X_FORWARDED_HOST' in request.META:
        response = HttpResponse()
        response["Content-Type"] = "image/jpeg"
        # response["Content-Disposition"] = 'attachment; filename*=UTF-8\'\'{0}'.format(
        #         archive.pretty_name)
        response['X-Accel-Redirect'] = "/image/{0}".format(archive.thumbnail.name)
        return response
    else:
        return HttpResponseRedirect(archive.thumbnail.url)


@login_required
def image_live_thumb(request: HttpRequest, archive_pk: int, position: int) -> HttpResponse:
    try:
        image = Image.objects.get(archive=archive_pk, position=position)
    except Image.DoesNotExist:
        raise Http404("Archive does not exist")
    if not image.archive.public and not request.user.is_authenticated:
        raise Http404("Archive does not exist")

    full_image = bool(request.GET.get("full", ''))

    image_data = image.fetch_image_data(use_original_image=full_image)
    if not image_data:
        return HttpResponse('')

    if request.GET.get("base64", ''):
        image_data_enconded = "data:image/jpeg;base64," + base64.b64encode(image_data).decode('utf-8')
        response = HttpResponse(image_data_enconded)
        response['Cache-Control'] = "max-age=86400"
    else:
        response = HttpResponse(image_data)
        response["Content-Type"] = "image/jpeg"
        response['Cache-Control'] = "max-age=86400"
    return response


@login_required
def extract_toggle(request: HttpRequest, pk: int) -> HttpResponse:
    """Extract archive toggle."""

    if not request.user.has_perm('viewer.expand_archive'):
        return render_error(request, "You don't have the permission to expand an Archive.")
    try:
        with transaction.atomic():
            archive = Archive.objects.select_for_update().get(pk=pk)
            logger.info('Toggling images for archive: {}'.format(archive.get_absolute_url()))
            archive.extract_toggle()
            if archive.extracted:
                action = 'EXPAND_ARCHIVE'
            else:
                action = 'REDUCE_ARCHIVE'
            event_log(
                request.user,
                action,
                content_object=archive,
                result='success'
            )
    except Archive.DoesNotExist:
        raise Http404("Archive does not exist")

    return HttpResponseRedirect(request.META["HTTP_REFERER"])


@login_required
def extract(request: HttpRequest, pk: int) -> HttpResponse:
    """Extract archive toggle."""

    if not request.user.has_perm('viewer.expand_archive'):
        return render_error(request, "You don't have the permission to expand an Archive.")
    try:
        with transaction.atomic():
            archive = Archive.objects.select_for_update().get(pk=pk)
            if archive.extracted:
                return render_error(request, "Archive is already extracted.")

            resized = bool(request.GET.get("resized", ''))

            if resized:
                logger.info('Expanding images (resized) for archive: {}'.format(archive.get_absolute_url()))
            else:
                logger.info('Expanding images for archive: {}'.format(archive.get_absolute_url()))

            archive.extract(resized=resized)
            action = 'EXPAND_ARCHIVE'
            event_log(
                request.user,
                action,
                content_object=archive,
                result='success'
            )
    except Archive.DoesNotExist:
        raise Http404("Archive does not exist")

    return HttpResponseRedirect(request.META["HTTP_REFERER"])


@login_required
def reduce(request: HttpRequest, pk: int) -> HttpResponse:
    """Reduce archive."""

    if not request.user.has_perm('viewer.expand_archive'):
        return render_error(request, "You don't have the permission to expand an Archive.")
    try:
        with transaction.atomic():
            archive = Archive.objects.select_for_update().get(pk=pk)
            if not archive.extracted:
                return render_error(request, "Archive is already reduced.")

            logger.info('Reducing images for archive: {}'.format(archive.get_absolute_url()))

            archive.reduce()
            action = 'REDUCE_ARCHIVE'
            event_log(
                request.user,
                action,
                content_object=archive,
                result='success'
            )
    except Archive.DoesNotExist:
        raise Http404("Archive does not exist")

    return HttpResponseRedirect(request.META["HTTP_REFERER"])


@login_required
def public(request: HttpRequest, pk: int) -> HttpResponse:
    """Public archive."""

    if not request.user.has_perm('viewer.publish_archive'):
        return render_error(request, "You don't have the permission to public an Archive.")

    try:
        with transaction.atomic():
            archive = Archive.objects.select_for_update().get(pk=pk)
            if archive.public:
                return render_error(request, "Archive is already public.")
            archive.set_public()
            logger.info('Setting public status to public for Archive: {}'.format(archive.get_absolute_url()))
            event_log(
                request.user,
                'PUBLISH_ARCHIVE',
                content_object=archive,
                result='published'
            )
    except Archive.DoesNotExist:
        raise Http404("Archive does not exist")

    return HttpResponseRedirect(request.META["HTTP_REFERER"])


@login_required
def private(request: HttpRequest, pk: int) -> HttpResponse:
    """Private archive."""

    if not request.user.has_perm('viewer.publish_archive'):
        return render_error(request, "You don't have the permission to private an Archive.")

    try:
        with transaction.atomic():
            archive = Archive.objects.select_for_update().get(pk=pk)
            if not archive.public:
                return render_error(request, "Archive is already private.")
            archive.set_private()
            logger.info('Setting public status to private for Archive: {}'.format(archive.get_absolute_url()))
            event_log(
                request.user,
                'UNPUBLISH_ARCHIVE',
                content_object=archive,
                result='unpublished'
            )
    except Archive.DoesNotExist:
        raise Http404("Archive does not exist")

    return HttpResponseRedirect(request.META["HTTP_REFERER"])


@login_required
def calculate_images_sha1(request: HttpRequest, pk: int) -> HttpResponse:
    """Calculate archive's images SHA1."""

    # TODO: Different permission
    if not request.user.has_perm('viewer.publish_archive'):
        return render_error(request, "You don't have the permission to calculate SHA1.")

    try:
        archive: Archive = Archive.objects.get(pk=pk)
    except Archive.DoesNotExist:
        raise Http404("Archive does not exist")

    logger.info('Calculating images SHA1 for Archive: {}'.format(archive.get_absolute_url()))
    if archive.image_set.filter(sha1__isnull=False).count() == 0:
        archive.calculate_sha1_for_images()

    return HttpResponseRedirect(request.META["HTTP_REFERER"])


@login_required
def recalc_info(request: HttpRequest, pk: int) -> HttpResponse:
    """Recalculate archive info."""

    if not request.user.is_staff:
        return render_error(request, "You need to be an admin to recalculate file info.")

    try:
        archive = Archive.objects.get(pk=pk)
    except Archive.DoesNotExist:
        raise Http404("Archive does not exist")

    logger.info('Recalculating file info for Archive: {}'.format(archive.get_absolute_url()))
    archive.recalc_fileinfo()
    archive.generate_image_set(force=False)
    archive.fix_image_positions()
    archive.generate_thumbnails()

    return HttpResponseRedirect(request.META["HTTP_REFERER"])


@login_required
def mark_similar_archives(request: HttpRequest, pk: int) -> HttpResponse:
    """Create similar info as marks for archive."""

    if not request.user.is_staff:
        return render_error(request, "You need to be an admin to mark similar archives.")

    try:
        archive = Archive.objects.get(pk=pk)
    except Archive.DoesNotExist:
        raise Http404("Archive does not exist")

    logger.info('Create similar info as marks for Archive: {}'.format(archive.get_absolute_url()))
    archive.create_marks_for_similar_archives()

    return HttpResponseRedirect(request.META["HTTP_REFERER"])


@login_required
def recall_api(request: HttpRequest, pk: int) -> HttpResponse:
    """Recall provider API, if possible."""

    if not request.user.has_perm('viewer.update_metadata'):
        return render_error(request, "You don't have the permission to refresh source metadata on an Archive.")

    try:
        archive = Archive.objects.get(pk=pk)
    except Archive.DoesNotExist:
        raise Http404("Archive does not exist")

    if not archive.gallery_id:
        return render_error(request, "No gallery associated with this archive.")

    gallery = Gallery.objects.get(pk=archive.gallery_id)

    current_settings = Settings(load_from_config=crawler_settings.config)

    if current_settings.workers.web_queue and gallery.provider:

        current_settings.set_update_metadata_options(providers=(gallery.provider,))

        def gallery_callback(x: Optional['Gallery'], crawled_url: Optional[str], result: str) -> None:
            event_log(
                request.user,
                'UPDATE_METADATA',
                content_object=x,
                result=result,
                data=crawled_url
            )

        current_settings.workers.web_queue.enqueue_args_list(
            (gallery.get_link(),),
            override_options=current_settings,
            gallery_callback=gallery_callback
        )

        logger.info(
            'Updating gallery API data for gallery: {} and related archives'.format(
                gallery.get_absolute_url()
            )
        )

    return HttpResponseRedirect(request.META["HTTP_REFERER"])


@login_required
def generate_matches(request: HttpRequest, pk: int) -> HttpResponse:
    """Generate matches for non-match."""

    if not request.user.is_staff:
        return render_error(request, "You need to be an admin to generate matches.")

    try:
        archive = Archive.objects.get(pk=pk)
    except Archive.DoesNotExist:
        raise Http404("Archive does not exist")

    if archive.gallery:
        return render_error(request, "Archive is already matched.")

    clear_title = True if 'clear' in request.GET else False

    provider_filter = request.GET.get('provider', '')
    try:
        cutoff = float(request.GET.get('cutoff', '0.4'))
    except ValueError:
        cutoff = 0.4
    try:
        max_matches = int(request.GET.get('max-matches', '10'))
    except ValueError:
        max_matches = 10

    archive.generate_possible_matches(
        clear_title=clear_title, provider_filter=provider_filter,
        cutoff=cutoff, max_matches=max_matches
    )
    archive.save()

    logger.info('Generated matches for {}, found {}'.format(
        archive.zipped.path,
        archive.possible_matches.count()
    ))

    return HttpResponseRedirect(request.META["HTTP_REFERER"])


@login_required
def rematch_archive(request: HttpRequest, pk: int) -> HttpResponse:
    """Match an Archive."""

    if not request.user.is_staff:
        return render_error(request, "You need to be an admin to rematch an archive.")

    try:
        archive = Archive.objects.get(pk=pk)
    except Archive.DoesNotExist:
        raise Http404("Archive does not exist")

    if archive.gallery:
        archive.gallery.archive_set.remove(archive)

    folder_crawler_thread = FolderCrawlerThread(
        crawler_settings, ['-frm', archive.zipped.path])
    folder_crawler_thread.start()

    logger.info('Rematching archive: {}'.format(archive.title))

    return HttpResponseRedirect(request.META["HTTP_REFERER"])


@login_required
def delete_archive(request: HttpRequest, pk: int) -> HttpResponse:
    """Delete archive and gallery data if there is any."""

    if not request.user.is_staff:
        return render_error(request, "You need to be an admin to delete an archive.")

    try:
        archive = Archive.objects.get(pk=pk)
    except Archive.DoesNotExist:
        raise Http404("Archive does not exist")

    if request.method == 'POST':

        p = request.POST
        if "delete_confirm" in p:

            message_list = list()

            if "delete-archive" in p:
                message_list.append('archive entry')
            if "delete-gallery" in p:
                message_list.append('associated gallery')
            if "delete-file" in p:
                message_list.append('associated file')

            message = 'For archive: {}, deleting: {}'.format(archive.title, ', '.join(message_list))

            logger.info("User {}: {}".format(request.user.username, message))
            messages.success(request, message)

            gallery = archive.gallery
            archive_report = archive.delete_text_report()

            user_reason = p.get('reason', '')

            # Mark deleted takes priority over delete
            if "mark-gallery-deleted" in p and archive.gallery:
                archive.gallery.mark_as_deleted()
                archive.gallery = None
            elif "delete-gallery" in p and archive.gallery:
                old_gallery_link = archive.gallery.get_link()
                archive.gallery.delete()
                archive.gallery = None
                event_log(
                    request.user,
                    'DELETE_GALLERY',
                    reason=user_reason,
                    data=old_gallery_link,
                    result='deleted',
                )
            if "delete-file" in p:
                archive.delete_all_files()
            if "delete-archive" in p:
                archive.delete_files_but_archive()
                archive.delete()

            event_log(
                request.user,
                'DELETE_ARCHIVE',
                reason=user_reason,
                content_object=gallery,
                result='deleted',
                data=archive_report
            )

            return HttpResponseRedirect(reverse('viewer:main-page'))

    d = {'archive': archive}

    return render(request, "viewer/include/delete_archive.html", d)


@login_required
def delete_manage_archive(request: HttpRequest, pk: int) -> HttpResponse:
    """Recalculate archive info."""

    if not request.user.has_perm('viewer.mark_archive'):
        return render_error(request, "You don't have the permission to mark an Archive.")

    try:
        archive_manage_entry = ArchiveManageEntry.objects.get(pk=pk)
    except ArchiveManageEntry.DoesNotExist:
        messages.error(request, "ArchiveManageEntry does not exist")
        return HttpResponseRedirect(request.META["HTTP_REFERER"])

    if archive_manage_entry.mark_user != request.user and not request.user.is_staff:
        return render_error(request, "You don't have the permission to delete this mark.")

    messages.success(request, 'Deleting ArchiveManageEntry for Archive: {}'.format(archive_manage_entry.archive))

    event_log(
        request.user,
        'DELETE_MANAGER_ARCHIVE',
        content_object=archive_manage_entry.archive,
        result='deleted'
    )

    archive_manage_entry.delete()

    return HttpResponseRedirect(request.META["HTTP_REFERER"])
