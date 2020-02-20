# -*- coding: utf-8 -*-
import unittest
import mock
from datetime import timedelta

from openprocurement.api.utils import get_now
from openprocurement.api.tests.base import snitch

from openprocurement.tender.belowthreshold.tests.base import test_lots, test_cancellation
from openprocurement.tender.belowthreshold.tests.cancellation import (
    TenderCancellationResourceTestMixin,
    TenderCancellationDocumentResourceTestMixin,
)
from openprocurement.tender.belowthreshold.tests.cancellation_blanks import (
    # TenderLotCancellationResourceTest
    create_tender_lot_cancellation,
    patch_tender_lot_cancellation,
    # TenderLotsCancellationResourceTest
    create_tender_lots_cancellation,
    patch_tender_lots_cancellation,
    create_tender_cancellation_after_19_04_2020,
    patch_tender_cancellation_after_19_04_2020,
)

from openprocurement.tender.openua.tests.base import BaseTenderUAContentWebTest, test_bids
from openprocurement.tender.openua.tests.cancellation_blanks import (
    # TenderAwardsCancellationResourceTest
    cancellation_active_award,
    cancellation_unsuccessful_award,
    # TenderCancellationResourceTest
    create_tender_cancellation,
    patch_tender_cancellation,
    create_tender_cancellation_before_19_04_2020,
    patch_tender_cancellation_before_19_04_2020,
)


class TenderCancellationResourceNewReleaseTestMixin(object):
    valid_reasonType_choices = ["noDemand", "unFixable", "forceMajeure", "expensesCut"]

    test_create_tender_cancellation_after_19_04_2020 = snitch(create_tender_cancellation_after_19_04_2020)
    test_patch_tender_cancellation_after_19_04_2020 = snitch(patch_tender_cancellation_after_19_04_2020)
    test_create_tender_cancellation_before_19_04_2020 = snitch(create_tender_cancellation_before_19_04_2020)
    test_patch_tender_cancellation_before_19_04_2020 = snitch(patch_tender_cancellation_before_19_04_2020)


class TenderCancellationResourceTest(
    BaseTenderUAContentWebTest,
    TenderCancellationResourceTestMixin,
    TenderCancellationResourceNewReleaseTestMixin
):
    test_create_tender_cancellation = snitch(create_tender_cancellation)
    test_patch_tender_cancellation = snitch(patch_tender_cancellation)


class TenderLotCancellationResourceTest(BaseTenderUAContentWebTest):
    initial_lots = test_lots

    test_create_tender_lot_cancellation = snitch(create_tender_lot_cancellation)
    test_patch_tender_lot_cancellation = snitch(patch_tender_lot_cancellation)


class TenderLotsCancellationResourceTest(BaseTenderUAContentWebTest):
    initial_lots = 2 * test_lots

    test_create_tender_lots_cancellation = snitch(create_tender_lots_cancellation)
    test_patch_tender_lots_cancellation = snitch(patch_tender_lots_cancellation)


class TenderAwardsCancellationResourceTest(BaseTenderUAContentWebTest):
    initial_lots = 2 * test_lots
    initial_status = "active.auction"
    initial_bids = test_bids

    test_cancellation_active_award = snitch(cancellation_active_award)
    test_cancellation_unsuccessful_award = snitch(cancellation_unsuccessful_award)


class TenderCancellationDocumentResourceTest(BaseTenderUAContentWebTest, TenderCancellationDocumentResourceTestMixin):
    def setUp(self):
        super(TenderCancellationDocumentResourceTest, self).setUp()
        # Create cancellation
        response = self.app.post_json(
            "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
            {"data": test_cancellation},
        )
        cancellation = response.json["data"]
        self.cancellation_id = cancellation["id"]


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TenderCancellationDocumentResourceTest))
    suite.addTest(unittest.makeSuite(TenderCancellationResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
