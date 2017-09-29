# -*- coding: utf-8 -*-
import os
from datetime import datetime, timedelta
from copy import deepcopy
from openprocurement.api.constants import SANDBOX_MODE
from openprocurement.api.utils import get_now
from openprocurement.tender.belowthreshold.tests.base import (
    test_tender_data as test_tender_data_api,
    now,
    test_features_tender_data,
    BaseTenderWebTest,
    test_bids as base_test_bids,
    test_organization,
)
test_tender_data = test_tender_ua_data = test_tender_data_api.copy()
test_tender_data['procurementMethodType'] = "aboveThresholdUA"
# test_tender_data["enquiryPeriod"] = {}
del test_tender_data["enquiryPeriod"]
test_tender_data["tenderPeriod"] = {
        "endDate": (now + timedelta(days=16)).isoformat()
}
test_tender_data["items"] = [{
        "description": u"футляри до державних нагород",
        "description_en": u"Cases for state awards",
        "classification": {
            "scheme": u"ДК021",
            "id": u"44617100-9",
            "description": u"Cartons"
        },
        "additionalClassifications": [
            {
                "scheme": u"ДКПП",
                "id": u"17.21.1",
                "description": u"папір і картон гофровані, паперова й картонна тара"
            }
        ],
        "unit": {
            "name": u"item",
            "code": u"44617100-9"
        },
        "quantity": 5,
        "deliveryDate": {
            "startDate": (now + timedelta(days=2)).isoformat(),
            "endDate": (now + timedelta(days=5)).isoformat()
        },
        "deliveryAddress": {
            "countryName": u"Україна",
            "postalCode": "79000",
            "region": u"м. Київ",
            "locality": u"м. Київ",
            "streetAddress": u"вул. Банкова 1"
            }
}]
test_features_bids = [
    {
        "parameters": [
            {
                "code": i["code"],
                "value": 0.1,
            }
            for i in test_features_tender_data['features']
        ],
        "tenderers": [
            test_organization
        ],
        "value": {
            "amount": 479,
            "currency": "UAH",
            "valueAddedTaxIncluded": True
        },
        'selfEligible': True, 'selfQualified': True,
    },
    {
        "parameters": [
            {
                "code": i["code"],
                "value": 0.15,
            }
            for i in test_features_tender_data['features']
        ],
        "tenderers": [
            test_organization
        ],
        "value": {
            "amount": 479,
            "currency": "UAH",
            "valueAddedTaxIncluded": True
        },
        'selfEligible': True, 'selfQualified': True,
    }
]
if SANDBOX_MODE:
    test_tender_data['procurementMethodDetails'] = 'quick, accelerator=1440'

test_bids = deepcopy(base_test_bids)
for i in test_bids:
    i.update({'selfEligible': True, 'selfQualified': True})


# test_tender_data["tenderPeriod"] = test_tender_data["enquiryPeriod"].copy()

test_features_tender_ua_data = test_features_tender_data.copy()
test_features_tender_ua_data['procurementMethodType'] = "aboveThresholdUA"
# test_features_tender_ua_data["enquiryPeriod"] = {}
del test_features_tender_ua_data["enquiryPeriod"]
test_features_tender_ua_data["tenderPeriod"] = {
        "endDate": (now + timedelta(days=16)).isoformat()
}
test_features_tender_ua_data["items"][0]["deliveryDate"] = test_tender_data["items"][0]["deliveryDate"]
test_features_tender_ua_data["items"][0]["deliveryAddress"] = test_tender_data["items"][0]["deliveryAddress"]
# test_features_tender_ua_data["tenderPeriod"] = test_features_tender_ua_data["enquiryPeriod"].copy()


from openprocurement.api.utils import apply_data_patch


class BaseTenderUAWebTest(BaseTenderWebTest):
    initial_data = test_tender_data
    initial_status = None
    initial_bids = None
    initial_lots = None
    relative_to = os.path.dirname(__file__)
    primary_tender_status = 'active.tendering'  # status, to which tender should be switched from 'draft'
    question_claim_block_status = 'active.auction'  # status, tender cannot be switched to while it has questions/complaints related to its lot
    forbidden_document_modification_actions_status = "active.auction"  # status, in which operations with tender documents (adding, updating) are forbidden
    forbidden_question_modification_actions_status = 'active.auction'  # status, in which adding/updating tender questions is forbidden
    forbidden_lot_actions_status = 'active.auction'  # status, in which operations with tender lots (adding, updating, deleting) are forbidden
    forbidden_contract_document_modification_actions_status = 'unsuccessful'  # status, in which operations with tender's contract documents (adding, updating) are forbidden
    forbidden_auction_actions_status = 'active.tendering'  # status, in which operations with tender auction (getting auction info, reporting auction results, updating auction urls) and adding tender documents are forbidden
    forbidden_auction_document_create_actions_status = 'active.tendering'  # status, in which adding document to tender auction is forbidden

    def go_to_enquiryPeriod_end(self):
        now = get_now()
        self.set_status('active.tendering', {
            "enquiryPeriod": {
                "startDate": (now - timedelta(days=13)).isoformat(),
                "endDate": (now - (timedelta(minutes=1) if SANDBOX_MODE else timedelta(days=1))).isoformat()
            },
            "tenderPeriod": {
                "startDate": (now - timedelta(days=13)).isoformat(),
                "endDate": (now + (timedelta(minutes=2) if SANDBOX_MODE else timedelta(days=2))).isoformat()
            },
            "auctionPeriod": {
                "startDate": (now + timedelta(days=2)).isoformat()
            }
        })

    def set_status(self, status, extra=None):
        data = {'status': status}
        if status == 'active.tendering':
            data.update({
                "enquiryPeriod": {
                    "startDate": (now).isoformat(),
                    "endDate": (now + timedelta(days=13)).isoformat()
                },
                "tenderPeriod": {
                    "startDate": (now).isoformat(),
                    "endDate": (now + timedelta(days=16)).isoformat()
                }
            })
        elif status == 'active.auction':
            data.update({
                "enquiryPeriod": {
                    "startDate": (now - timedelta(days=16)).isoformat(),
                    "endDate": (now - timedelta(days=3)).isoformat()
                },
                "tenderPeriod": {
                    "startDate": (now - timedelta(days=16)).isoformat(),
                    "endDate": (now).isoformat()
                },
                "auctionPeriod": {
                    "startDate": (now).isoformat()
                }
            })
            if self.initial_lots:
                data.update({
                    'lots': [
                        {
                            "auctionPeriod": {
                                "startDate": (now).isoformat()
                            }
                        }
                        for i in self.initial_lots
                    ]
                })
        elif status == 'active.qualification':
            data.update({
                "enquiryPeriod": {
                    "startDate": (now - timedelta(days=17)).isoformat(),
                    "endDate": (now - timedelta(days=4)).isoformat()
                },
                "tenderPeriod": {
                    "startDate": (now - timedelta(days=17)).isoformat(),
                    "endDate": (now - timedelta(days=1)).isoformat()
                },
                "auctionPeriod": {
                    "startDate": (now - timedelta(days=1)).isoformat(),
                    "endDate": (now).isoformat()
                },
                "awardPeriod": {
                    "startDate": (now).isoformat()
                }
            })
            if self.initial_lots:
                data.update({
                    'lots': [
                        {
                            "auctionPeriod": {
                                "startDate": (now - timedelta(days=1)).isoformat(),
                                "endDate": (now).isoformat()
                            }
                        }
                        for i in self.initial_lots
                    ]
                })
        elif status == 'active.awarded':
            data.update({
                "enquiryPeriod": {
                    "startDate": (now - timedelta(days=17)).isoformat(),
                    "endDate": (now - timedelta(days=4)).isoformat()
                },
                "tenderPeriod": {
                    "startDate": (now - timedelta(days=17)).isoformat(),
                    "endDate": (now - timedelta(days=1)).isoformat()
                },
                "auctionPeriod": {
                    "startDate": (now - timedelta(days=1)).isoformat(),
                    "endDate": (now).isoformat()
                },
                "awardPeriod": {
                    "startDate": (now).isoformat(),
                    "endDate": (now).isoformat()
                }
            })
            if self.initial_lots:
                data.update({
                    'lots': [
                        {
                            "auctionPeriod": {
                                "startDate": (now - timedelta(days=1)).isoformat(),
                                "endDate": (now).isoformat()
                            }
                        }
                        for i in self.initial_lots
                    ]
                })
        elif status == 'complete':
            data.update({
                "enquiryPeriod": {
                    "startDate": (now - timedelta(days=25)).isoformat(),
                    "endDate": (now - timedelta(days=11)).isoformat()
                },
                "tenderPeriod": {
                    "startDate": (now - timedelta(days=25)).isoformat(),
                    "endDate": (now - timedelta(days=8)).isoformat()
                },
                "auctionPeriod": {
                    "startDate": (now - timedelta(days=8)).isoformat(),
                    "endDate": (now - timedelta(days=7)).isoformat()
                },
                "awardPeriod": {
                    "startDate": (now - timedelta(days=7)).isoformat(),
                    "endDate": (now - timedelta(days=7)).isoformat()
                }
            })
            if self.initial_lots:
                data.update({
                    'lots': [
                        {
                            "auctionPeriod": {
                                "startDate": (now - timedelta(days=8)).isoformat(),
                                "endDate": (now - timedelta(days=7)).isoformat()
                            }
                        }
                        for i in self.initial_lots
                    ]
                })
        if extra:
            data.update(extra)

        tender = self.db.get(self.tender_id)
        tender.update(apply_data_patch(tender, data))
        self.db.save(tender)

        authorization = self.app.authorization
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.get('/tenders/{}'.format(self.tender_id))
        self.app.authorization = authorization
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        return response


class BaseTenderUAContentWebTest(BaseTenderUAWebTest):
    initial_data = test_tender_data
    initial_status = None
    initial_bids = None
    initial_lots = None

    def setUp(self):
        super(BaseTenderUAContentWebTest, self).setUp()
        self.create_tender()
