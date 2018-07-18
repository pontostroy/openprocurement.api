# -*- coding: utf-8 -*-
import unittest
from copy import deepcopy

from openprocurement.api.tests.base import snitch

from openprocurement.tender.belowthreshold.tests.base import (
    test_organization,
    test_lots
)
from openprocurement.tender.belowthreshold.tests.auction_blanks import (
    # TenderSameValueAuctionResourceTest
    post_tender_auction_reversed,
    post_tender_auction_not_changed,
    # TenderFeaturesAuctionResourceTest
    get_tender_auction_feature,
    post_tender_auction_feature,
    # TenderFeaturesLotAuctionResourceTest
    get_tender_lot_auction_features,
    post_tender_lot_auction_features,
    # TenderFeaturesMultilotAuctionResourceTest
    get_tender_lots_auction_features,
    post_tender_lots_auction_features,
    # TenderAuctionResourceTestMixin
    get_tender_auction_not_found,
    get_tender_auction,
    patch_tender_auction,
    post_tender_auction_document,
    # TenderLotAuctionResourceTestMixin
    get_tender_lot_auction,
    patch_tender_lot_auction,
    post_tender_lot_auction_document,
    # TenderMultipleLotAuctionResourceTestMixin
    get_tender_lots_auction,
    post_tender_lots_auction_document,
)
from openprocurement.frameworkagreement.cfaua.constants import MIN_BIDS_NUMBER
from openprocurement.tender.openeu.tests.auction_blanks import (
    # TenderMultipleLotAuctionResourceTest
    patch_tender_2lot_auction,
)
from openprocurement.frameworkagreement.cfaua.tests.base import (
    BaseTenderContentWebTest,
    test_features_tender_data,
    test_bids
)
from openprocurement.frameworkagreement.cfaua.tests.auction_blanks import (
    # TenderAuctionResourceTest
    post_tender_auction_all_awards_pending,
    # TenderAuctionResourceTestMixin
    post_tender_auction,
    # TenderLotAuctionResourceTestMixin
    post_tender_lot_auction,
    # TenderMultipleLotAuctionResourceTestMixin
    post_tender_lots_auction
)


one_lot_restriction = True


class TenderAuctionResourceTestMixin(object):
    test_get_tender_auction_not_found = snitch(get_tender_auction_not_found)
    test_get_tender_auction = snitch(get_tender_auction)
    test_post_tender_auction = snitch(post_tender_auction)
    test_patch_tender_auction = snitch(patch_tender_auction)
    test_post_tender_auction_document = snitch(post_tender_auction_document)


class TenderLotAuctionResourceTestMixin(object):
    test_get_tender_auction = snitch(get_tender_lot_auction)
    test_post_tender_auction = snitch(post_tender_lot_auction)
    test_patch_tender_auction = snitch(patch_tender_lot_auction)
    test_post_tender_auction_document = snitch(post_tender_lot_auction_document)


class TenderMultipleLotAuctionResourceTestMixin(object):
    test_get_tender_auction = snitch(get_tender_lots_auction)
    test_post_tender_auction = snitch(post_tender_lots_auction)
    test_post_tender_auction_document = snitch(post_tender_lots_auction_document)


class TenderAuctionResourceTest(BaseTenderContentWebTest, TenderAuctionResourceTestMixin):
    #initial_data = tender_data
    initial_auth = ('Basic', ('broker', ''))
    initial_bids = test_bids

    def setUp(self):
        super(TenderAuctionResourceTest, self).setUp()
        # switch to active.pre-qualification
        self.time_shift('active.pre-qualification')
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {"data": {"id": self.tender_id}})
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.json['data']['status'], "active.pre-qualification")

        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.get('/tenders/{}/qualifications?acc_token={}'.format(self.tender_id, self.tender_token))
        for qualific in response.json['data']:
            response = self.app.patch_json('/tenders/{}/qualifications/{}?acc_token={}'.format(
                self.tender_id, qualific['id'], self.tender_token), {'data': {"status": "active", "qualified": True, "eligible": True}})
            self.assertEqual(response.status, '200 OK')

        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(self.tender_id, self.tender_token),
                                       {"data": {"status": "active.pre-qualification.stand-still"}})
        self.assertEqual(response.status, "200 OK")
        # # switch to active.pre-qualification.stand-still


class TenderAuctionBidsOverMaxAwards(TenderAuctionResourceTest):
    initial_bids = test_bids + deepcopy(test_bids)  # double testbids
    min_bids_number = MIN_BIDS_NUMBER * 2


class TenderFrameworkResourceTest(TenderAuctionResourceTest):
    test_post_tender_auction_all_awards_pending = snitch(post_tender_auction_all_awards_pending)


class TenderSameValueAuctionResourceTest(BaseTenderContentWebTest):

    initial_status = 'active.auction'
    tenderer_info = deepcopy(test_organization)
    initial_bids = [
        {
            "tenderers": [
                tenderer_info
            ],
            "value": {
                "amount": 469,
                "currency": "UAH",
                "valueAddedTaxIncluded": True
            },
            'selfQualified': True,
            'selfEligible': True
        }
        for i in range(MIN_BIDS_NUMBER)
    ]

    def setUp(self):
        super(TenderSameValueAuctionResourceTest, self).setUp()
        auth = self.app.authorization
        # switch to active.pre-qualification
        self.set_status('active.pre-qualification', {'status': 'active.tendering'})
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {"data": {"id": self.tender_id}})
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.json['data']['status'], "active.pre-qualification")
        self.app.authorization = auth

        response = self.app.get('/tenders/{}/qualifications'.format(self.tender_id))
        for qualific in response.json['data']:
            response = self.app.patch_json('/tenders/{}/qualifications/{}'.format(
                self.tender_id, qualific['id']), {'data': {"status": "active", "qualified": True, "eligible": True}})
            self.assertEqual(response.status, '200 OK')

        # switch to active.pre-qualification.stand-still
        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(self.tender_id, self.tender_token),
                                       {"data": {"status": "active.pre-qualification.stand-still"}})
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.json['data']['status'], "active.pre-qualification.stand-still")

        # switch to active.auction
        self.set_status('active.auction', {'status': 'active.pre-qualification.stand-still'})
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {"data": {"id": self.tender_id}})
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.json['data']['status'], "active.auction")
        self.app.authorization = auth

    test_post_tender_auction_not_changed = snitch(post_tender_auction_not_changed)
    test_post_tender_auction_reversed = snitch(post_tender_auction_reversed)


class TenderLotAuctionResourceTest(TenderLotAuctionResourceTestMixin, TenderAuctionResourceTest):
    initial_lots = test_lots
    # initial_data = test_tender_data


class TenderLotAuctionBidsOverMaxAwards(TenderLotAuctionResourceTest):
    initial_bids = test_bids + deepcopy(test_bids)  # double testbids
    min_bids_number = MIN_BIDS_NUMBER * 2


# TODO: Remove if will be approved.
@unittest.skipIf(one_lot_restriction, "CFAUA not allow more than one lot per tender.")
class TenderMultipleLotAuctionResourceTest(TenderMultipleLotAuctionResourceTestMixin, TenderAuctionResourceTest):
    initial_lots = 2 * test_lots

    test_patch_tender_auction = snitch(patch_tender_2lot_auction)


class TenderFeaturesAuctionResourceTest(TenderAuctionResourceTest):
    initial_data = test_features_tender_data
    tenderer_info = deepcopy(test_organization)
    initial_bids = [
        {
            "parameters": [
                {
                    "code": i["code"],
                    "value": 0.15 if x == 1 else 0.1,
                }
                for i in test_features_tender_data['features']
            ],
            "tenderers": [
                tenderer_info
            ],
            "value": {
                "amount": 469 + x * 1,
                "currency": "UAH",
                "valueAddedTaxIncluded": True
            },
            'selfQualified': True,
            'selfEligible': True
        } for x in range(TenderAuctionResourceTest.min_bids_number)
    ]

    test_get_tender_auction = snitch(get_tender_auction_feature)
    test_post_tender_auction = snitch(post_tender_auction_feature)


class TenderFeaturesLotAuctionResourceTest(TenderLotAuctionResourceTestMixin, TenderFeaturesAuctionResourceTest):
    initial_lots = test_lots
    test_get_tender_auction = snitch(get_tender_lot_auction_features)
    test_post_tender_auction = snitch(post_tender_lot_auction_features)


# TODO: Remove if will be approved.
@unittest.skipIf(one_lot_restriction, "CFAUA not allow more than one lot per tender.")
class TenderFeaturesMultilotAuctionResourceTest(TenderMultipleLotAuctionResourceTestMixin,
                                                TenderFeaturesAuctionResourceTest):
    initial_lots = test_lots * 2
    test_get_tender_auction = snitch(get_tender_lots_auction_features)
    test_post_tender_auction = snitch(post_tender_lots_auction_features)
    test_patch_tender_auction = snitch(patch_tender_2lot_auction)


# TODO: Remove if will be approved.
@unittest.skipIf(one_lot_restriction, "CFAUA not allow more than one lot per tender.")
class TenderMultilotAuctionBidsOverMaxAwards(TenderFeaturesMultilotAuctionResourceTest):
    tenderer_info = deepcopy(test_organization)
    initial_bids = [
        {
            "parameters": [
                {
                    "code": i["code"],
                    "value": 0.15 if x == 1 else 0.1,
                }
                for i in test_features_tender_data['features']
            ],
            "tenderers": [
                tenderer_info
            ],
            "value": {
                "amount": 469 + x * 1,
                "currency": "UAH",
                "valueAddedTaxIncluded": True
            },
            'selfQualified': True,
            'selfEligible': True
        } for x in range(TenderAuctionResourceTest.min_bids_number * 2)
    ]
    min_bids_number = TenderAuctionResourceTest.min_bids_number * 2  # double min bids number


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TenderAuctionResourceTest))
    suite.addTest(unittest.makeSuite(TenderSameValueAuctionResourceTest))
    suite.addTest(unittest.makeSuite(TenderFeaturesAuctionResourceTest))
    suite.addTest(unittest.makeSuite(TenderFrameworkResourceTest))
    suite.addTest(unittest.makeSuite(TenderAuctionBidsOverMaxAwards))
    suite.addTest(unittest.makeSuite(TenderLotAuctionBidsOverMaxAwards))
    suite.addTest(unittest.makeSuite(TenderMultilotAuctionBidsOverMaxAwards))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
