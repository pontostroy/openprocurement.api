# -*- coding: utf-8 -*-
from openprocurement.api.utils import json_view, APIResource, context_unpack
from openprocurement.agreement.core.utils import save_agreement
from openprocurement.agreement.core.resource import agreements_resource
from openprocurement.relocation.api.utils import (
    extract_transfer,
    update_ownership,
    save_transfer,
    get_transfer_location,
)
from openprocurement.relocation.api.validation import (
    validate_ownership_data,
    validate_agreement_accreditation_level,
    validate_agreement_owner_accreditation_level,
    validate_agreement,
    validate_agreement_transfer_token,
)


@agreements_resource(
    name="Agreement ownership", path="/agreements/{agreement_id}/ownership", description="Agreements Ownership"
)
class AgreementResource(APIResource):
    @json_view(
        permission="view_agreement",
        validators=(
            validate_agreement_accreditation_level,
            validate_agreement_owner_accreditation_level,
            validate_ownership_data,
            validate_agreement,
            validate_agreement_transfer_token,
        ),
    )
    def post(self):
        agreement = self.request.validated["agreement"]
        data = self.request.validated["ownership_data"]

        route_name = "{}.Agreement".format(agreement.agreementType)
        location = get_transfer_location(self.request, route_name, agreement_id=agreement.id)
        transfer = extract_transfer(self.request, transfer_id=data["id"])

        if transfer.get("usedFor") and transfer.get("usedFor") != location:
            self.request.errors.add("body", "transfer", "Transfer already used")
            self.request.errors.status = 403
            return

        update_ownership(agreement, transfer)
        self.request.validated["agreement"] = agreement

        transfer.usedFor = location
        self.request.validated["transfer"] = transfer

        if save_transfer(self.request):
            self.LOGGER.info(
                "Updated transfer relation {}".format(transfer.id),
                extra=context_unpack(self.request, {"MESSAGE_ID": "transfer_relation_update"}),
            )

            if save_agreement(self.request):
                self.LOGGER.info(
                    "Updated ownership of agreement {}".format(agreement.id),
                    extra=context_unpack(self.request, {"MESSAGE_ID": "agreement_ownership_update"}),
                )

                return {"data": agreement.serialize("view")}
