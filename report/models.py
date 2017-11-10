from __future__ import unicode_literals

from django.db import models
import datetime
# Create your models here.
class result(models.Model):
    report_id = models.CharField(max_length=20,default='',null=True)
    title = models.CharField(max_length=100,default='',null=True)
    url = models.CharField(max_length=100,default='',null=True)
    username = models.CharField(max_length=100,default='',null=True)
    username_url = models.CharField(max_length=100,default='',null=True)
    state = models.CharField(max_length=20,default='',null=True)
    substate = models.CharField(max_length=20,default='',null=True)
    severity_rating = models.CharField(max_length=20,default='',null=True)
    created_at = models.CharField(max_length=40,default='',null=True)
    team_name = models.CharField(max_length=100,default='',null=True)
    team_url = models.CharField(max_length=40,default='',null=True)
    team_about = models.TextField(default='',null=True)
    has_bounty = models.CharField(max_length=20,default='',null=True)
    can_view_team = models.CharField(max_length=20,default='',null=True)
    is_external_bug = models.CharField(max_length=20,default='',null=True)
    is_participant = models.CharField(max_length=20,default='',null=True)
    public = models.CharField(max_length=20,default='',null=True)
    visibility = models.CharField(max_length=20,default='',null=True)
    cve_ids = models.CharField(max_length=40,default='',null=True)
    singular_disclosure_disabled = models.CharField(max_length=40,default='',null=True)
    disclosed_at = models.CharField(max_length=40,default='',null=True)
    bug_reporter_agreed_on_going_public_at = models.CharField(max_length=40,default='',null=True)
    team_member_agreed_on_going_public_at = models.CharField(max_length=40,default='',null=True)
    comments_closed = models.CharField(max_length=40,default='',null=True)
    vulnerability_information = models.TextField(default='',null=True)
    vulnerability_information_html = models.TextField(default='',null=True)
    original_report_id = models.CharField(max_length=40,null=True)
    original_report_url= models.CharField(max_length=40,null=True)
    allow_singular_disclosure_at = models.CharField(max_length=40,default='',null=True)
    allow_singular_disclosure_after = models.CharField(max_length=40,default='',null=True)
    singular_disclosure_allowed = models.CharField(max_length=40,default='',null=True)
    vote_count = models.CharField(max_length=40,default='',null=True)
    def __unicode__(self): 
        return self.title

    
class dialogue(models.Model):
    report_id = models.CharField(max_length=10,default='',null=True)
    activity_id = models.CharField(max_length=10,default='',null=True)
    is_internal = models.CharField(max_length=10,default='',null=True)
    editable = models.CharField(max_length=10,default='',null=True)
    type =  models.CharField(max_length=10,default='',null=True)
    message = models.TextField(default='',null=True)
    markdown_message = models.TextField(default='',null=True)
    automated_response = models.CharField(max_length=10,default='',null=True)
    created_at = models.CharField(max_length=40,default='',null=True)
    updated_at = models.CharField(max_length=40,default='',null=True)
    actor_username = models.CharField(max_length=40,default='',null=True)
    actor_url = models.CharField(max_length=40,default='',null=True)
    genius_execution_id = models.CharField(max_length=40,null=True)
    team_handle = models.CharField(max_length=40,default='',null=True)
    

class summary(models.Model):
    pages = models.CharField(max_length=30,default='',null=True)
    total_reports = models.CharField(max_length=30,default='',null=True)
    create_time = models.DateTimeField(default=datetime.datetime.now())
class summar(models.Model):              
    report_id = models.CharField(max_length=20,null=True)
    summaries_id = models.CharField(max_length=30,default='',null=True)
    content = models.TextField(default='',null=True)
    content_html = models.TextField(default='',null=True)
    category = models.CharField(max_length=30,default='',null=True)
    can_view = models.CharField(max_length=30,default='',null=True)
    can_create = models.CharField(max_length=30,default='',null=True)