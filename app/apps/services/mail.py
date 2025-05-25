import hashlib
import logging
import os.path
import re

import magic
from apps.main.services import MORCoreService
from apps.main.templatetags.melding_tags import get_bijlagen
from django.conf import settings
from django.contrib.sites.models import Site
from django.core.mail import EmailMultiAlternatives, SafeMIMEMultipart
from django.template.loader import get_template
from django.urls import reverse

logger = logging.getLogger(__name__)


class EmailMultiRelated(EmailMultiAlternatives):
    """
    A version of EmailMessage that makes it easy to send multipart/related
    messages. For example, including text and HTML versions with inline images.

    @see https://djangosnippets.org/snippets/2215/
    """

    related_subtype = "related"

    def __init__(self, *args, **kwargs):
        # self.related_ids = []
        self.related_attachments = []
        return super().__init__(*args, **kwargs)

    def attach_related(self, filename, content, mimetype):
        self.related_attachments.append((filename, content, mimetype))

    def attach_related_file(self, path):
        """Attaches a file from the filesystem."""
        filename = os.path.basename(path)
        content = open(path, "rb").read()
        mime = magic.Magic(mime=True)
        mimetype = mime.from_file(path)
        self.attach_related(filename, content, mimetype)

    def _create_message(self, msg):
        return self._create_attachments(
            self._create_related_attachments(self._create_alternatives(msg))
        )

    def _create_alternatives(self, msg):
        for i, (content, mimetype) in enumerate(self.alternatives):
            if mimetype == "text/html":
                for related_attachment in self.related_attachments:
                    filename, _, _ = related_attachment
                    content = re.sub(
                        r"(?<!cid:)%s" % re.escape(filename),
                        "cid:%s" % filename,
                        content,
                    )
                self.alternatives[i] = (content, mimetype)

        return super()._create_alternatives(msg)

    def _create_related_attachments(self, msg):
        encoding = self.encoding or settings.DEFAULT_CHARSET
        if self.related_attachments:
            body_msg = msg
            msg = SafeMIMEMultipart(_subtype=self.related_subtype, encoding=encoding)
            if self.body:
                msg.attach(body_msg)
            for related_attachment in self.related_attachments:
                msg.attach(self._create_related_attachment(*related_attachment))
        return msg

    def _create_related_attachment(self, filename, content, mimetype=None):
        """
        Convert the filename, content, mimetype triple into a MIME attachment
        object. Adjust headers to use Content-ID where applicable.
        Taken from http://code.djangoproject.com/ticket/4771
        """
        attachment = super()._create_attachment(filename, content, mimetype)
        if filename:
            mimetype = attachment["Content-Type"]
            del attachment["Content-Type"]
            del attachment["Content-Disposition"]
            attachment.add_header("Content-Disposition", "inline", filename=filename)
            attachment.add_header("Content-Type", mimetype, name=filename)
            attachment.add_header("Content-ID", "<%s>" % filename)
        return attachment


class MailService:
    def taak_aangemaakt_email(
        self,
        taak,
        meldingalias=None,
        template_stijl="html",
        verzenden=False,
        base_url=None,
    ):
        send_to = []

        domain = Site.objects.get_current().domain
        url_basis = f"{settings.PROTOCOL}://{domain}{settings.PORT}"
        # @ TODO retrieve taaktype data from taakr
        taaktype = taak.taaktype

        bijlagen = get_bijlagen(taak.melding.response_json)

        bijlagen_flat = [
            url
            for url in reversed(
                [b.get("afbeelding") for b in bijlagen if b.get("afbeelding")]
            )
        ]

        email_context = {
            "melding": meldingalias,
            "taak": taak,
            "taaktype": taaktype,
            "bijlagen": [b.split("/")[-1].replace(" ", "_") for b in bijlagen_flat],
            "url_basis": url_basis,
        }

        taak_id_hash = hashlib.sha256(
            (str(taak.id) + settings.SECRET_HASH_KEY).encode()
        ).hexdigest()

        # Construct the feedback URLs using base_url
        niet_opgelost_url = f"{base_url}{reverse('feedback', kwargs={'taak_id': taak.id, 'email_hash': taak_id_hash})}"
        email_context.update(
            {
                "niet_opgelost_url": niet_opgelost_url,
            }
        )

        if taak.taaktype.externe_instantie_email:
            send_to.append(taak.taaktype.externe_instantie_email)

        text_template = get_template("email/email_taak_aangemaakt_geen_knop.txt")
        html_template = get_template("email/email_taak_aangemaakt_geen_knop.html")
        text_content = text_template.render(email_context)
        html_content = html_template.render(email_context)
        subject = f"De gemeente Rotterdam heeft een melding met nummer {taak.taak_zoek_data.bron_signaal_ids[0] if taak.taak_zoek_data.bron_signaal_ids else ''} van een bewoner ontvangen waarvan de taakafhandeling onder de verantwoordelijkheid valt van uw organisatie."
        msg = EmailMultiRelated(
            subject, text_content, settings.DEFAULT_FROM_EMAIL, send_to
        )
        msg.attach_alternative(html_content, "text/html")

        for bijlage in bijlagen_flat:
            filename = bijlage.split("/")[-1].replace(
                " ", "_"
            )  # be careful with file names
            file_path = os.path.join("/media/", filename)
            bijlage_response = MORCoreService().bestand_halen(bijlage)
            with open(file_path, "wb") as f:
                f.write(bijlage_response.content)
            msg.attach_related_file(file_path)

        if send_to and not settings.DEBUG and verzenden:
            msg.send()
        elif settings.DEBUG and verzenden and settings.DEVELOPER_EMAIL:
            msg = EmailMultiRelated(
                subject,
                text_content,
                settings.DEFAULT_FROM_EMAIL,
                [
                    settings.DEVELOPER_EMAIL,
                ],
            )
            msg.attach_alternative(html_content, "text/html")
            for bijlage in bijlagen_flat:
                filename = bijlage.split("/")[-1].replace(
                    " ", "_"
                )  # be careful with file names
                file_path = os.path.join("/media/", filename)
                bijlage_response = MORCoreService().bestand_halen(bijlage)
                with open(file_path, "wb") as f:
                    f.write(bijlage_response.content)
                msg.attach_related_file(file_path)
            msg.send()
        if template_stijl == "html":
            return html_content
        return text_content
