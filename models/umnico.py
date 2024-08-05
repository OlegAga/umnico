#!/usr/bin/env python3

import logging
import os

import requests
from odoo import models

logger = logging.getLogger("Umnico")


class ResponseWrapper:
    def __init__(self, response):
        self.response = response
        self.status_code = response.status_code
        self.ok = response.ok
        self.data = self._parse_data()

    def _parse_data(self):
        try:
            return self.response.json()
        except ValueError:
            return self.response.text

    def is_success(self):
        return self.ok

    def get_data(self):
        return self.data

    def get_status_code(self):
        return self.status_code


class Umnico(models.Model):
    """Webhook for Umnico."""

    _inherit = "webhook"

    baseUrl = os.environ.get(
        "UMNICO_BASE_URL",
        "https://api.umnico.com",
    )
    authHeader = {
        "Authorization": "Bearer "
        + os.environ.get(
            "UMNICO_AUTH_HEADER",
        )
    }
    accountId = int(os.environ.get("UMNICO_AUTH_HEADER"))

    def set_account_id(self):
        """Get Account."""
        try:
            response = requests.get(
                f"{self.baseUrl}/v1.3/account/me",
                headers=self.authHeader,
            )
            wrapped_response = ResponseWrapper(response)
            if wrapped_response.is_success():
                result = wrapped_response.get_data()
                logger.debug(f"Success: {result}")
                assert result.get("account", {}).get("status") == "active"
                self.accountId = result.get("account", {}).get("id")
                return wrapped_response.get_data()
            else:
                logger.error(
                    f"Error: {wrapped_response.get_status_code()} - {wrapped_response.get_data()}"
                )
                return None
        except requests.RequestException as e:
            logger.error(f"Request failed: {e}")
            return None
        except AssertionError as e:
            logger.error(f"Status failed: {e}")
            return None

    def create_webhook_umnico(self, url, name):
        """Create hook."""
        try:
            response = requests.post(
                f"{self.baseUrl}/v1.3/webhooks/",
                json={"url": url, "name": name},
                headers=self.authHeader,
            )
            wrapped_response = ResponseWrapper(response)
            if wrapped_response.is_success():
                logger.info(f"Success: {wrapped_response.get_data()}")
                return wrapped_response.get_data()
            else:
                logger.error(
                    f"Error: {wrapped_response.get_status_code()} - {wrapped_response.get_data()}"
                )
                return None
        except requests.RequestException as e:
            logger.error(f"Request failed: {e}")
            return None

    def list_webhook_umnico(self):
        """List hook."""
        try:
            response = requests.get(
                f"{self.baseUrl}/v1.3/webhooks/",
                headers=self.authHeader,
            )
            wrapped_response = ResponseWrapper(response)
            if wrapped_response.is_success():
                logger.info(f"Success: {wrapped_response.get_data()}")
                return wrapped_response.get_data()
            else:
                logger.error(
                    f"Error: {wrapped_response.get_status_code()} - {wrapped_response.get_data()}"
                )
                return None
        except requests.RequestException as e:
            logger.error(f"Request failed: {e}")
            return None

    def change_webhook_umnico(self, id, url, name, status):
        """Change hook.
        status: 1 or 0
        """
        try:
            response = requests.put(
                f"{self.baseUrl}/v1.3/webhooks/{id}",
                json={"url": url, "name": name, "status": status},
                headers=self.authHeader,
            )
            wrapped_response = ResponseWrapper(response)
            if wrapped_response.is_success():
                logger.info(f"Success: {wrapped_response.get_data()}")
                return wrapped_response.get_data()
            else:
                logger.error(
                    f"Error: {wrapped_response.get_status_code()} - {wrapped_response.get_data()}"
                )
                return None
        except requests.RequestException as e:
            logger.error(f"Request failed: {e}")
            return None

    def delete_webhook_umnico(self, id):
        """Delete hook."""
        try:
            response = requests.delete(
                f"{self.baseUrl}/v1.3/webhooks/{id}",
                headers=self.authHeader,
            )
            wrapped_response = ResponseWrapper(response)
            if wrapped_response.is_success():
                logger.info(f"Success: {wrapped_response.get_data()}")
                return wrapped_response.get_data()
            else:
                logger.error(
                    f"Error: {wrapped_response.get_status_code()} - {wrapped_response.get_data()}"
                )
                return None
        except requests.RequestException as e:
            logger.error(f"Request failed: {e}")
            return None

    def create_external_id(self, obj, eid):
        vals = {
            "model": obj._name,
            "module": "umnico",
            "name": eid,
            "res_id": obj.id,
            "noupdate": True,
        }
        self.env["ir.model.data"].create(vals)

    def create_lead(self, lead_id, message):
        # After need map message object like https://api.umnico.com/docs/ru/apiMethods/history.html#message-object
        # with crm.lead object from /odoo/addons/crm/models/crm_lead.py at firstly
        try:
            assert lead_id
            vals = {}
            lead = self.env["crm.lead"].create(vals)
            self.create_external_id(lead, lead_id)
        except Exception as e:
            logger.error(f"Smtng wrong during lead create. {e}")

    def create_customer(self, message):
        try:
            customer_id = message.get("sender", {}).get("customerId")
            assert customer_id
            vals = {}
            customer = self.env["res.partner"].create(vals)
            self.create_external_id(customer, customer_id)
        except Exception as e:
            logger.error(f"Smtng wrong during customer create. {e}")

    def run_umnico_message_incoming(self):
        """Handle hook message.incoming type."""
        try:
            result = self.env.request.jsonrequest
            logger.debug(f"Hook is: {result}")
            assert result.get("type") == "message.incoming"
            assert result.get("accountId") == self.accountId
            if result.get("isNewLead") is True:
                self.create_lead(
                    result.get("leadId"),
                    result.get("message"),
                )
            elif result.get("isNewCustomer") is True:
                self.create_customer(result.get("message"))
        except AssertionError:
            logger.error(f"Type or account failed.")
            return None

    def run_webhook_umnico_message_outgoing(self):
        pass

    def run_webhook_umnico_lead_created(self):
        pass

    def run_webhook_umnico_lead_changed(self):
        pass

    def run_webhook_umnico_lead_changed_status(self):
        pass

    def run_webhook_umnico_customer_created(self):
        pass

    def run_webhook_umnico_customer_changed(self):
        pass

    def run_webhook_umnico_integration_created(self):
        pass

    def run_webhook_umnico_integration_removed(self):
        pass
