import hashlib
import logging
import os.path
import re

import magic
from django.conf import settings
from django.core.files.storage import default_storage
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
        bestanden=[],
        request=None,
    ):
        send_to = []
        taaktype = taak.taaktype

        email_context = {
            "melding": meldingalias,
            "taak": taak,
            "taaktype": taaktype,
            "bijlagen": bestanden,
        }

        if taaktype.externe_instantie_feedback_vereist:
            taak_id_hash = hashlib.sha256(
                (str(taak.id) + settings.SECRET_HASH_KEY).encode()
            ).hexdigest()

            # Construct the feedback URLs
            opgelost_url = request.build_absolute_uri(
                reverse(
                    "feedback",
                    kwargs={
                        "taak_id": taak.id,
                        "email_hash": taak_id_hash,
                        "email_feedback_type": 1,
                    },
                )
            )
            niet_opgelost_url = request.build_absolute_uri(
                reverse(
                    "feedback",
                    kwargs={
                        "taak_id": taak.id,
                        "email_hash": taak_id_hash,
                        "email_feedback_type": 0,
                    },
                )
            )
            email_context.update(
                {
                    "opgelost_url": opgelost_url,
                    "niet_opgelost_url": niet_opgelost_url,
                }
            )

        if taak.taaktype.externe_instantie_email:
            send_to.append(taak.taaktype.externe_instantie_email)

        text_template = get_template("email/email_taak_aangemaakt_geen_feedback_2.txt")
        html_template = get_template("email/email_taak_aangemaakt_geen_feedback_2.html")
        text_content = text_template.render(email_context)
        html_content = html_template.render(email_context)
        subject = f"Taaktype: {taaktype} - taak aangemaakt"
        msg = EmailMultiRelated(
            subject, text_content, settings.DEFAULT_FROM_EMAIL, send_to
        )
        msg.attach_alternative(html_content, "text/html")

        for f in bestanden:
            attachment = default_storage.path(f)
            msg.attach_related_file(attachment)

        if send_to and not settings.DEBUG and verzenden:
            msg.send()
        if template_stijl == "html":
            with open(
                os.path.join(settings.BASE_DIR, "test_template.html"), "w"
            ) as file:
                file.write(html_content)
            return html_content
        return text_content
