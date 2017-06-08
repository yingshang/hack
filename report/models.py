from __future__ import unicode_literals

from django.db import models
import datetime
# Create your models here.
class result(models.Model):
    report_id = models.CharField(max_length=20,default='')
    title = models.CharField(max_length=100,default='')
    url = models.CharField(max_length=100,default='')
    username = models.CharField(max_length=100,default='',null=True)
    username_url = models.CharField(max_length=100,default='')
    state = models.CharField(max_length=20,default='')
    substate = models.CharField(max_length=20,default='')
    severity_rating = models.CharField(max_length=20,default='')
    created_at = models.CharField(max_length=40,default='')
    team_name = models.CharField(max_length=100,default='')
    team_url = models.CharField(max_length=40,default='')
    team_about = models.TextField(default='')
    has_bounty = models.CharField(max_length=20,default='')
    can_view_team = models.CharField(max_length=20,default='')
    is_external_bug = models.CharField(max_length=20,default='')
    is_participant = models.CharField(max_length=20,default='')
    public = models.CharField(max_length=20,default='')
    visibility = models.CharField(max_length=20,default='')
    cve_ids = models.CharField(max_length=40,default='')
    singular_disclosure_disabled = models.CharField(max_length=40,default='')    
    disclosed_at = models.CharField(max_length=40,default='')
    bug_reporter_agreed_on_going_public_at = models.CharField(max_length=40,default='',null=True)
    team_member_agreed_on_going_public_at = models.CharField(max_length=40,default='',null=True)
    comments_closed = models.CharField(max_length=40,default='')
    vulnerability_information = models.TextField(default='')
    vulnerability_information_html = models.TextField(default='')
    original_report_id = models.CharField(max_length=40,null=True)
    original_report_url= models.CharField(max_length=40,null=True)
    allow_singular_disclosure_at = models.CharField(max_length=40,default='')
    allow_singular_disclosure_after = models.CharField(max_length=40,default='')
    singular_disclosure_allowed = models.CharField(max_length=40,default='')
    vote_count = models.CharField(max_length=40,default='')  
    def __unicode__(self): 
        return self.title

    
class dialogue(models.Model):
    report_id = models.CharField(max_length=10,default='')
    activity_id = models.CharField(max_length=10,default='')
    is_internal = models.CharField(max_length=10,default='')
    editable = models.CharField(max_length=10,default='')
    type =  models.CharField(max_length=10,default='')
    message = models.TextField(default='',null=True)
    markdown_message = models.TextField(default='',null=True)
    automated_response = models.CharField(max_length=10,default='')
    created_at = models.CharField(max_length=40,default='')
    updated_at = models.CharField(max_length=40,default='')
    actor_username = models.CharField(max_length=40,default='')
    actor_url = models.CharField(max_length=40,default='')
    genius_execution_id = models.CharField(max_length=40,null=True)
    team_handle = models.CharField(max_length=40,default='')
    

class summary(models.Model):
    pages = models.CharField(max_length=30,default='')
    total_reports = models.CharField(max_length=30,default='')
    create_time = models.DateTimeField(default=datetime.datetime.now())
class summar(models.Model):              
    report_id = models.CharField(max_length=20)
    summaries_id = models.CharField(max_length=30,default='')
    content = models.TextField(default='')
    content_html = models.TextField(default='')
    category = models.CharField(max_length=30,default='')
    can_view = models.CharField(max_length=30,default='')
    can_create = models.CharField(max_length=30,default='')