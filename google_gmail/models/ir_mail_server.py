# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import base64
import logging
import smtplib
import threading

from odoo import api, models, tools, _
from odoo.exceptions import UserError
from odoo.tools import pycompat, ustr

_logger = logging.getLogger(__name__)

SMTP_TIMEOUT = 60


class IrMailServer(models.Model):
    """Represents an SMTP server, able to send outgoing emails, with SSL and TLS capabilities."""

    _name = 'ir.mail_server'
    _inherit = ['ir.mail_server', 'google.gmail.mixin']

    @api.onchange('smtp_encryption')
    def _onchange_encryption(self):
        """Do not change the SMTP configuration if it's a Gmail server

        (e.g. the port which is already set)"""
        if not self.use_google_gmail_service:
            super()._onchange_encryption()

    @api.onchange('use_google_gmail_service')
    def _onchange_use_google_gmail_service(self):
        if self.use_google_gmail_service:
            self.smtp_host = 'smtp.gmail.com'
            self.smtp_encryption = 'starttls'
            self.smtp_port = 587
        else:
            self.google_gmail_authorization_code = False
            self.google_gmail_refresh_token = False
            self.google_gmail_access_token = False
            self.google_gmail_access_token_expiration = False

    # LEFTOVER METHOD FROM VERSION 14.0
    # def _smtp_login(self, connection, smtp_user, smtp_password):
    #     if len(self) == 1 and self.use_google_gmail_service:
    #         auth_string = self._generate_oauth2_string(smtp_user, self.google_gmail_refresh_token)
    #         oauth_param = base64.b64encode(auth_string.encode()).decode()
    #         connection.ehlo()
    #         connection.docmd('AUTH', 'XOAUTH2 %s' % oauth_param)
    #     else:
    #         super(IrMailServer, self)._smtp_login(connection, smtp_user, smtp_password)

    # OVERWRITTEN CONNECT METHOD TO INCORPORATE LOGIC FROM _SMTP_LOGIN METHOD
    def connect(self, host=None, port=None, user=None, password=None, encryption=None,
                smtp_debug=False, mail_server_id=None):
        """Returns a new SMTP connection to the given SMTP server.
           When running in test mode, this method does nothing and returns `None`.

           :param host: host or IP of SMTP server to connect to, if mail_server_id not passed
           :param int port: SMTP port to connect to
           :param user: optional username to authenticate with
           :param password: optional password to authenticate with
           :param string encryption: optional, ``'ssl'`` | ``'starttls'``
           :param bool smtp_debug: toggle debugging of SMTP sessions (all i/o
                              will be output in logs)
           :param mail_server_id: ID of specific mail server to use (overrides other parameters)
        """
        # Do not actually connect while running in test mode
        if getattr(threading.currentThread(), 'testing', False):
            return None

        mail_server = smtp_encryption = None
        if mail_server_id:
            mail_server = self.sudo().browse(mail_server_id)
        elif not host:
            mail_server = self.sudo().search([], order='sequence', limit=1)

        if mail_server:
            smtp_server = mail_server.smtp_host
            smtp_port = mail_server.smtp_port
            smtp_user = mail_server.smtp_user
            smtp_password = mail_server.smtp_pass
            smtp_encryption = mail_server.smtp_encryption
            smtp_debug = smtp_debug or mail_server.smtp_debug
        else:
            # we were passed individual smtp parameters or nothing and there is no default server
            smtp_server = host or tools.config.get('smtp_server')
            smtp_port = tools.config.get('smtp_port', 25) if port is None else port
            smtp_user = user or tools.config.get('smtp_user')
            smtp_password = password or tools.config.get('smtp_password')
            smtp_encryption = encryption
            if smtp_encryption is None and tools.config.get('smtp_ssl'):
                smtp_encryption = 'starttls' # smtp_ssl => STARTTLS as of v7

        if not smtp_server:
            raise UserError(
                (_("Missing SMTP Server") + "\n" +
                 _("Please define at least one SMTP server, "
                   "or provide the SMTP parameters explicitly.")))

        if smtp_encryption == 'ssl':
            if 'SMTP_SSL' not in smtplib.__all__:
                raise UserError(
                    _("Your Odoo Server does not support SMTP-over-SSL. "
                      "You could use STARTTLS instead. "
                       "If SSL is needed, an upgrade to Python 2.6 on the server-side "
                       "should do the trick."))
            connection = smtplib.SMTP_SSL(smtp_server, smtp_port, timeout=SMTP_TIMEOUT)
        else:
            connection = smtplib.SMTP(smtp_server, smtp_port, timeout=SMTP_TIMEOUT)
        connection.set_debuglevel(smtp_debug)
        if smtp_encryption == 'starttls':
            # starttls() will perform ehlo() if needed first
            # and will discard the previous list of services
            # after successfully performing STARTTLS command,
            # (as per RFC 3207) so for example any AUTH
            # capability that appears only on encrypted channels
            # will be correctly detected for next step
            connection.starttls()

        if smtp_user:
            # Attempt authentication - will raise if AUTH service not supported
            # The user/password must be converted to bytestrings in order to be usable for
            # certain hashing schemes, like HMAC.
            # See also bug #597143 and python issue #5285
            smtp_user = pycompat.to_native(ustr(smtp_user))

            # ====================== CHANGED PART ======================

            # smtp_password = pycompat.to_native(ustr(smtp_password))
            # connection.login(smtp_user, smtp_password)

            if mail_server and mail_server.use_google_gmail_service:
                auth_string = mail_server._generate_oauth2_string(smtp_user, mail_server.google_gmail_refresh_token)
                oauth_param = base64.b64encode(auth_string.encode()).decode()
                connection.ehlo()
                connection.docmd('AUTH', 'XOAUTH2 %s' % oauth_param)

            # ================== END OF CHANGED PART ==================

        return connection
