# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models, _
from odoo.exceptions import UserError
from imaplib import IMAP4, IMAP4_SSL
from poplib import POP3, POP3_SSL

MAIL_TIMEOUT = 60


class FetchmailServer(models.Model):
    _name = 'fetchmail.server'
    _inherit = ['fetchmail.server', 'google.gmail.mixin']

    @api.constrains('use_google_gmail_service', 'type')
    def _check_use_google_gmail_service(self):
        if any(server.use_google_gmail_service and server.type != 'imap' for server in self):
            raise UserError(_('Gmail authentication only supports IMAP server type.'))

    @api.onchange('use_google_gmail_service')
    def _onchange_use_google_gmail_service(self):
        """Set the default configuration for a IMAP Gmail server."""
        if self.use_google_gmail_service:
            self.server = 'imap.gmail.com'
            self.type = 'imap'
            self.is_ssl = True
            self.port = 993
        else:
            self.google_gmail_authorization_code = False
            self.google_gmail_refresh_token = False
            self.google_gmail_access_token = False
            self.google_gmail_access_token_expiration = False

    # LEFTOVER METHOD FROM VERSION 14.0
    # def _imap_login(self, connection):
    #     """Authenticate the IMAP connection.
    #
    #     If the mail server is Gmail, we use the OAuth2 authentication protocol.
    #     """
    #     self.ensure_one()
    #     if self.use_google_gmail_service:
    #         auth_string = self._generate_oauth2_string(self.user, self.google_gmail_refresh_token)
    #         connection.authenticate('XOAUTH2', lambda x: auth_string)
    #         connection.select('INBOX')
    #     else:
    #         super(FetchmailServer, self)._imap_login(connection)

    # OVERWRITTEN CONNECT METHOD TO INCORPORATE LOGIC FROM _IMAP_LOGIN METHOD
    @api.multi
    def connect(self):
        self.ensure_one()
        if self.type == 'imap':
            if self.is_ssl:
                connection = IMAP4_SSL(self.server, int(self.port))
            else:
                connection = IMAP4(self.server, int(self.port))

            # ====================== CHANGED PART ======================

            # connection.login(self.user, self.password)
            self.ensure_one()
            if self.use_google_gmail_service:
                auth_string = self._generate_oauth2_string(self.user, self.google_gmail_refresh_token)
                connection.authenticate('XOAUTH2', lambda x: auth_string)
                connection.select('INBOX')

            # ================== END OF CHANGED PART ==================

        elif self.type == 'pop':
            if self.is_ssl:
                connection = POP3_SSL(self.server, int(self.port))
            else:
                connection = POP3(self.server, int(self.port))
            # TODO: use this to remove only unread messages
            # connection.user("recent:"+server.user)
            connection.user(self.user)
            connection.pass_(self.password)
        # Add timeout on socket
        connection.sock.settimeout(MAIL_TIMEOUT)
        return connection
