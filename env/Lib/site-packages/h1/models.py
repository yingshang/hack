# Copyright (c) 2016 Uber Technologies, Inc.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from __future__ import print_function, unicode_literals, division, absolute_import

import datetime as dt
import decimal
import json
import six

import dateutil.parser

_type_hydrators = {}


def list_model_types():
    return _type_hydrators.keys()


def hydrate_objects(objs, requester=None):
    return [hydrate_object(obj, requester) for obj in objs]


def hydrate_object(obj, requester=None):
    if obj is None:
        return None
    hydrator = _type_hydrators.get(obj["type"], None)
    if not callable(hydrator):
        raise Exception("Can't hydrate a %s!" % obj["type"])
    return hydrator(requester, obj)


class HackerOneEncoder(json.JSONEncoder):
    """
    JSONEncoder subclass that leverages an object's `__json__()` method,
    if available, to obtain its default JSON representation.
    """
    def default(self, obj):
        if hasattr(obj, '__json__'):
            return obj.__json__()
        return json.JSONEncoder.default(self, obj)


class _HydrationRegistrant(type):
    def __init__(cls, name, bases, nmspc):
        super(_HydrationRegistrant, cls).__init__(name, bases, nmspc)
        h1_type = getattr(cls, "TYPE", None)
        if h1_type:
            _type_hydrators[h1_type] = cls


@six.add_metaclass(_HydrationRegistrant)
class HackerOneObject(object):
    # subclasses will automatically register themselves
    # as the hydrator for their `TYPE`

    TYPE = None

    def __init__(self, requester, raw_data):
        self._requester = requester
        self._raw_data = raw_data

        self._handle_data()

    @property
    def id(self):
        return self._id

    @property
    def raw_data(self):
        return self._raw_data

    def _handle_data(self):
        assert(self.TYPE == self._raw_data["type"])
        self._id = self._raw_data.get("id", None)
        self._hydrate()

    def _hydrate(self):
        raise NotImplementedError()

    def _hydrate_verbatim(self, val):
        return val

    def _hydrate_datetime(self, val):
        if val is None:
            return None
        return dateutil.parser.parse(val)

    def _hydrate_decimal(self, val):
        return decimal.Decimal(val)

    def _hydrate_list_of_objects(self, val):
        return [self._hydrate_object(x) for x in val]

    def _hydrate_object(self, val):
        return hydrate_object(val, self._requester)

    def _make_attribute(self, attr_name, hydrator, optional=False):
        attrs = self._raw_data["attributes"]
        if optional and attr_name not in attrs:
            attr_val = None
        else:
            attr_val = attrs[attr_name]
        setattr(self, attr_name, hydrator(attr_val))

    def _make_relationship(self, rel_name, hydrator, default=None):
        # Some relationships are omitted if non-existent (like assignee)
        rels = self._raw_data["relationships"]
        rel_val = rels.get(rel_name, None)
        if rel_val is not None:
            rel_val = hydrator(rel_val["data"])
        elif default is not None:
            rel_val = default
        setattr(self, rel_name, rel_val)

    def __eq__(self, other):
        if not isinstance(other, HackerOneObject):
            return False
        if other.TYPE != self.TYPE:
            return False
        if self.id is None:
            return False
        if self.id != other.id:
            return False
        return True

    def __hash__(self):
        if self.id is None:
            return object.__hash__(self)
        return hash((self.TYPE, self.id))

    def __repr__(self):
        if self.id is None:
            return object.__repr__(self)
        return "<%s - %s>" % (self.__class__.__name__, self.id)

    def __json__(self):
        return self.raw_data


class HackerOneResource(HackerOneObject):
    RESOURCE_NAME = None

    def __init__(self, requester, raw_data):
        super(HackerOneResource, self).__init__(requester, raw_data)

    @classmethod
    def make_url(cls, obj_id):
        assert cls.RESOURCE_NAME
        return "/%s/%s" % (cls.RESOURCE_NAME, obj_id)

    @classmethod
    def get(cls, requester, obj_id):
        return requester.request_object(cls.make_url(obj_id))

    @classmethod
    def find(cls, requester, sort=None, yield_pages=False, **kwargs):
        query = {"filter": {}}
        if sort:
            query["sort"] = sort
        for key, val in kwargs.items():
            if isinstance(val, dt.datetime):
                val = val.strftime("%Y-%m-%dT%H:%M:%S.000Z")
            query["filter"][key] = val

        return requester.request_paginated_objects(
            "/%s" % cls.RESOURCE_NAME,
            query,
            yield_pages
        )

    @property
    def url(self):
        return self.make_url(self.id)

    @property
    def _canonical(self):
        return self._raw_data.get("_canonical", False)

    def try_complete(self):
        # TODO: property magic to do this automagically
        # when a field is missing
        if not self._canonical:
            self._fetch_canonical()

    def _fetch_canonical(self):
        self._raw_data = self._requester.request_json(self.url)["data"]
        self._raw_data["_canonical"] = True
        self._hydrate()

    def _hydrate(self):
        raise NotImplementedError()


class Report(HackerOneResource):
    TYPE = "report"
    RESOURCE_NAME = "reports"

    STATES = {
        "new",
        "triaged",
        "needs-more-info",
        "resolved",
        "not-applicable",
        "informative",
        "duplicate",
        "spam",
    }

    @property
    def total_bounty(self):
        if not self.bounties:
            return None
        return sum(b.amount for b in self.bounties)

    @property
    def total_payout(self):
        if not self.bounties:
            return None
        return self.total_bounty + sum(b.bonus_amount for b in self.bounties)

    @property
    def time_to_bounty(self):
        if not self.bounties:
            return None
        return self.bounties[0].created_at - self.created_at

    @property
    def time_to_closed(self):
        if not self.closed_at:
            return None
        return self.closed_at - self.created_at

    @property
    def time_to_first_response(self):
        if not self.first_program_activity_at:
            return None
        return self.first_program_activity_at - self.created_at

    @property
    def html_url(self):
        return "https://hackerone.com/reports/%s" % self.id

    def _hydrate(self):
        self._make_attribute("created_at", self._hydrate_datetime)
        self._make_attribute("last_activity_at", self._hydrate_datetime)
        self._make_attribute("last_program_activity_at", self._hydrate_datetime)
        self._make_attribute("last_reporter_activity_at", self._hydrate_datetime)
        self._make_attribute("triaged_at", self._hydrate_datetime)
        self._make_attribute("swag_awarded_at", self._hydrate_datetime)
        self._make_attribute("bounty_awarded_at", self._hydrate_datetime)
        self._make_attribute("closed_at", self._hydrate_datetime)
        self._make_attribute("disclosed_at", self._hydrate_datetime)
        self._make_attribute("title", self._hydrate_verbatim)
        self._make_attribute("first_program_activity_at", self._hydrate_datetime)
        self._make_attribute("state", self._hydrate_verbatim)
        self._make_attribute(
            "vulnerability_information",
            self._hydrate_verbatim,
            optional=True,
        )
        self._make_attribute(
            "issue_tracker_reference_id",
            self._hydrate_verbatim,
            optional=True,
        )
        self._make_attribute(
            "issue_tracker_reference_url",
            self._hydrate_verbatim,
            optional=True,
        )

        self._make_relationship("reporter", self._hydrate_object)
        self._make_relationship("assignee", self._hydrate_object)
        self._make_relationship("program", self._hydrate_object)
        self._make_relationship("bounties", self._hydrate_list_of_objects, [])
        self._make_relationship("activities", self._hydrate_list_of_objects, [])
        self._make_relationship("attachments", self._hydrate_list_of_objects, [])
        self._make_relationship("swag", self._hydrate_list_of_objects, [])
        self._make_relationship("vulnerability_types", self._hydrate_list_of_objects, [])
        self._make_relationship("summaries", self._hydrate_list_of_objects, [])


class User(HackerOneObject):
    TYPE = "user"

    def _hydrate(self):
        self._make_attribute("username", self._hydrate_verbatim)
        self._make_attribute("name", self._hydrate_verbatim)
        self._make_attribute("disabled", self._hydrate_verbatim)
        self._make_attribute("created_at", self._hydrate_datetime)
        self._make_attribute("profile_picture", self._hydrate_verbatim)

    def __str__(self):
        return self.username

    def __repr__(self):
        return "<%s - %s>" % (self.__class__.__name__, self.username)


class Program(HackerOneObject):
    TYPE = "program"

    def _hydrate(self):
        self._make_attribute("handle", self._hydrate_verbatim)
        self._make_attribute("created_at", self._hydrate_datetime)
        self._make_attribute("updated_at", self._hydrate_datetime)


class Bounty(HackerOneObject):
    TYPE = "bounty"

    def _hydrate(self):
        self._make_attribute("created_at", self._hydrate_datetime)
        self._make_attribute("bonus_amount", self._hydrate_decimal)
        self._make_attribute("amount", self._hydrate_decimal)


class VulnerabilityType(HackerOneObject):
    TYPE = "vulnerability-type"

    def _hydrate(self):
        self._make_attribute("name", self._hydrate_verbatim)
        self._make_attribute("description", self._hydrate_verbatim)
        self._make_attribute("created_at", self._hydrate_datetime)


class Attachment(HackerOneObject):
    TYPE = "attachment"

    def _hydrate(self):
        self._make_attribute("file_name", self._hydrate_verbatim)
        self._make_attribute("content_type", self._hydrate_verbatim)
        self._make_attribute("file_size", self._hydrate_verbatim)
        self._make_attribute("expiring_url", self._hydrate_verbatim)
        self._make_attribute("created_at", self._hydrate_datetime)


class ReportSummary(HackerOneObject):
    TYPE = "report-summary"

    def _hydrate(self):
        self._make_attribute("content", self._hydrate_verbatim)
        self._make_attribute("category", self._hydrate_verbatim)
        self._make_attribute("created_at", self._hydrate_datetime)
        self._make_attribute("updated_at", self._hydrate_datetime)

        self._make_relationship("user", self._hydrate_object)


class Group(HackerOneObject):
    TYPE = "group"

    def _hydrate(self):
        self._make_attribute("name", self._hydrate_verbatim)
        self._make_attribute("created_at", self._hydrate_datetime)


class Swag(HackerOneObject):
    TYPE = "swag"

    def _hydrate(self):
        self._make_attribute("sent", self._hydrate_verbatim)
        self._make_attribute("created_at", self._hydrate_datetime)

        self._make_relationship("address", self._hydrate_object)


class Address(HackerOneObject):
    TYPE = "address"

    def _hydrate(self):
        self._make_attribute("name", self._hydrate_verbatim)
        self._make_attribute("street", self._hydrate_verbatim)
        self._make_attribute("city", self._hydrate_verbatim)
        self._make_attribute("postal_code", self._hydrate_verbatim)
        self._make_attribute("state", self._hydrate_verbatim)
        self._make_attribute("country", self._hydrate_verbatim)
        self._make_attribute("tshirt_size", self._hydrate_verbatim, optional=True)
        self._make_attribute("phone_number", self._hydrate_verbatim, optional=True)
        self._make_attribute("created_at", self._hydrate_datetime)


class ActivityBase(HackerOneObject):
    def _hydrate(self):
        self._make_attribute("message", self._hydrate_verbatim, optional=True)
        self._make_attribute("internal", self._hydrate_verbatim)
        self._make_attribute("created_at", self._hydrate_datetime)
        self._make_attribute("updated_at", self._hydrate_datetime)

        self._make_relationship("actor", self._hydrate_object)
        self._make_relationship("attachments", self._hydrate_list_of_objects, [])

        self._activity_hydrate()

    def _activity_hydrate(self):
        pass


class ActivityStateChange(ActivityBase):
    pass


class ActivityPublicAgreement(ActivityBase):
    TYPE = "activity-agreed-on-going-public"


class ActivityBountyBase(ActivityBase):
    def _activity_hydrate(self):
        self._make_attribute("bounty_amount", self._hydrate_decimal)
        self._make_attribute("bonus_amount", self._hydrate_decimal)


class ActivityBountyAwarded(ActivityBase):
    TYPE = "activity-bounty-awarded"


class ActivityBountySuggested(ActivityBountyBase):
    TYPE = "activity-bounty-suggested"


class ActivityBugCloned(ActivityBase):
    TYPE = "activity-bug-cloned"

    def _activity_hydrate(self):
        # TODO: The API documentation seems to disagree with
        # what's actually being sent back here?
        self._make_attribute("original_report_id", self._hydrate_verbatim, optional=True)


class ActivityBugDuplicate(ActivityStateChange):
    TYPE = "activity-bug-duplicate"

    def _activity_hydrate(self):
        self._make_attribute("original_report_id", self._hydrate_verbatim, optional=True)


class ActivityBugInformative(ActivityStateChange):
    TYPE = "activity-bug-informative"


class ActivityBugNeedsMoreInfo(ActivityStateChange):
    TYPE = "activity-bug-needs-more-info"


class ActivityBugNew(ActivityStateChange):
    TYPE = "activity-bug-new"


class ActivityBugNotApplicable(ActivityStateChange):
    TYPE = "activity-bug-not-applicable"


class ActivityBugReopened(ActivityStateChange):
    TYPE = "activity-bug-reopened"


class ActivityBugResolved(ActivityStateChange):
    TYPE = "activity-bug-resolved"


class ActivityBugSpam(ActivityStateChange):
    TYPE = "activity-bug-spam"


class ActivityBugTriaged(ActivityStateChange):
    TYPE = "activity-bug-triaged"


class ActivityComment(ActivityBase):
    TYPE = "activity-comment"


class ActivityCommentsClosed(ActivityBase):
    TYPE = "activity-comments-closed"


class ActivityExternalUserInvitationCancelled(ActivityBase):
    TYPE = "activity-external-user-invitation-cancelled"

    def _activity_hydrate(self):
        self._make_attribute("email", self._hydrate_verbatim)


class ActivityExternalUserInvited(ActivityBase):
    TYPE = "activity-external-user-invited"

    def _activity_hydrate(self):
        self._make_attribute("email", self._hydrate_verbatim)


class ActivityExternalUserJoined(ActivityBase):
    TYPE = "activity-external-user-joined"

    def _activity_hydrate(self):
        self._make_attribute("duplicate_report_id", self._hydrate_verbatim)


class ActivityExternalUserRemoved(ActivityBase):
    TYPE = "activity-external-user-removed"

    def _activity_hydrate(self):
        self._make_relationship("removed_user", self._hydrate_object)


class ActivityGroupAssignedToBug(ActivityBase):
    TYPE = "activity-group-assigned-to-bug"

    def _activity_hydrate(self):
        self._make_relationship("group", self._hydrate_object)


class ActivityHackerRequestedMediation(ActivityBase):
    TYPE = "activity-hacker-requested-mediation"


class ActivityManuallyDisclosed(ActivityBase):
    TYPE = "activity-manually-disclosed"


class ActivityMediationRequested(ActivityBase):
    TYPE = "activity-mediation-requested"


class ActivityNotEligibleForBounty(ActivityBase):
    TYPE = "activity-not-eligible-for-bounty"


class ActivityReferenceIDAdded(ActivityBase):
    TYPE = "activity-reference-id-added"

    def _activity_hydrate(self):
        self._make_attribute("reference", self._hydrate_verbatim)
        self._make_attribute("reference_url", self._hydrate_verbatim)


class ActivityReportBecamePublic(ActivityBase):
    TYPE = "activity-report-became-public"


class ActivityReportTitleUpdated(ActivityBase):
    TYPE = "activity-report-title-updated"


class ActivityReportVulnerabilityTypesUpdated(ActivityBase):
    TYPE = "activity-report-vulnerability-types-updated"

    def _activity_hydrate(self):
        self._make_relationship("old_vulnerability_types", self._hydrate_list_of_objects, [])
        self._make_relationship("new_vulnerability_types", self._hydrate_list_of_objects, [])


class ActivityReportSeverityUpdated(ActivityBase):
    TYPE = "activity-report-severity-updated"


class ActivitySwagAwarded(ActivityBase):
    TYPE = "activity-swag-awarded"

    def _activity_hydrate(self):
        self._make_relationship("swag", self._hydrate_object)


class ActivityUserAssignedToBug(ActivityBase):
    TYPE = "activity-user-assigned-to-bug"

    def _activity_hydrate(self):
        self._make_relationship("assigned_user", self._hydrate_object)


class ActivityUserBannedFromProgram(ActivityBase):
    TYPE = "activity-user-banned-from-program"

    def _activity_hydrate(self):
        self._make_relationship("removed_user", self._hydrate_object)
