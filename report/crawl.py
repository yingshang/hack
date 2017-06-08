# -*- coding: utf-8 -*-
import requests
import time
import json
from models import *
def get_url(page):
    time.sleep(2) # sometimes hackerone block us
    url = "https://hackerone.com/hacktivity?sort_type=latest_disclosable_activity_at&filter=type%3Apublic&page="+str(page)
    headers = {
                        'Accept':'application/json, text/javascript, */*; q=0.01',
                        'content-type':'application/json',
                        'authority':'hackerone.com',
                        'x-requested-with':'XMLHttpRequest',
}
    r = requests.get(url = url,headers=headers,timeout=100)
    data = json.loads(r.content)    
    return data
def get_content(url):
    time.sleep(2) # sometimes hackerone block us
    headers = {
                        'Accept':'application/json, text/javascript, */*; q=0.01',
                        'content-type':'application/json',
                        'authority':'hackerone.com',
                        'x-requested-with':'XMLHttpRequest',
}
    r = requests.get(url = url,headers=headers,timeout=100)
    result = json.loads(r.content)
    return result
def get_page():
    data = get_url(1)
    pages = data['pages']
    total_reports = data['count']
    summary.objects.create(pages=pages,total_reports=total_reports)
    return pages
def resu(pages):
    #sec = 1
    for i in range(1, pages):
        #sec = sec +1
       # if (sec%40==1):
          #  time.sleep(10)
        print i
        data = get_url (i)    
        reports = data['reports']
        for report in reports:
            report_id = report['id']
            report_title = report['title']
            
            url = "https://hackerone.com"+report['url']         
            try:
                severity_rating = report['severity_rating']
            except KeyError:
                severity_rating = "none" 
            #try:
            data = get_content(url)
            #except requests.exceptions.Timeout:
            try:
                state = data['state']
            except KeyError:
                state="none"
            try:
                substate = data['substate']
            except KeyError:
                substate="none"
            created_at = data['created_at']         
            try:
                username = data['reporter']['username']
                username_url  ="https://hackerone.com"+ data['reporter']['url']
            except TypeError:
                username = "null"
                username_url = ""
            team_name = data['team']['handle']
            team_url = data['team']['url']
            team_about = data['team']['profile']['about']
            has_bounty = data['has_bounty?']
            can_view_team = data['can_view_team']
            is_external_bug = data['is_external_bug']
            is_participant = data['is_participant']
            public = data['public']
            visibility = data['visibility']
            cve_ids = data['cve_ids']
            singular_disclosure_disabled = data['singular_disclosure_disabled']
            disclosed_at = data['disclosed_at']
            bug_reporter_agreed_on_going_public_at = data['bug_reporter_agreed_on_going_public_at']
            team_member_agreed_on_going_public_at = data['team_member_agreed_on_going_public_at']
            comments_closed = data['comments_closed?']
            vulnerability_information = data['vulnerability_information']
            vulnerability_information_html = data['vulnerability_information_html']
            original_report_id = data['original_report_id']
            original_report_url = data['original_report_url']
            try:
                allow_singular_disclosure_at = data['allow_singular_disclosure_at']
            except KeyError:
                allow_singular_disclosure_at = "none"
            try:
                allow_singular_disclosure_after = data['allow_singular_disclosure_after']
            except KeyError:
                allow_singular_disclosure_after = "none"
            try:
                singular_disclosure_allowed = data['singular_disclosure_allowed']
            except KeyError:
                allow_singular_disclosure_after = "none"
            vote_count = data['vote_count']
            if result.objects.get_or_create(report_id=report_id)[1]:
                for summarie in data['summaries']:
                    try:
                        summaries_id = summarie['id']
                    except KeyError:
                        summaries_id = "none"
                    try:
                        content = summarie['content']
                    except KeyError:
                        content = "none"
                    try:
                        content_html = summarie['content_html']
                    except KeyError:
                        content_html = "none"
                    try:
                        category = summarie['category']
                    except KeyError:
                        category = "none"
                    try:
                        can_view = summarie['can_view?']
                    except KeyError:
                        can_view = "none"
                    try:
                        can_create = summarie['can_create?']
                    except KeyError:
                        can_create = "none"
                    summar.objects.create(
                                                 report_id = report_id,
                                                 summaries_id = summaries_id,
                                                 content = content,
                                                 content_html = content_html,
                                                 )
                    
                    
                for activity in data['activities']:
                    activity_id = activity['id']
                    is_internal = activity['is_internal']
                    editable = activity['editable']
                    type = activity['type']
                    message = activity['message']
                    markdown_message = activity['markdown_message']
                    automated_response = activity['automated_response']
                    created_at = activity['created_at']
                    updated_at = activity['updated_at']
                    try:
                        actor_username = activity['actor_username']
                    except KeyError:
                        actor_username = "none"
                    try:
                        actor_url = activity['actor_url']
                    except KeyError:
                        actor_url = "none"
                    genius_execution_id = activity['genius_execution_id']
                    team_handle = activity['team_handle']
                    dialogue.objects.create(
                                            report_id = report_id,
                                            activity_id = activity_id,
                                            is_internal = is_internal,
                                            editable = editable,
                                            type = type,
                                            message = message,
                                            markdown_message = markdown_message,
                                            automated_response = automated_response,
                                            created_at = created_at,
                                            updated_at = updated_at,
                                            actor_username = actor_username,
                                            actor_url = actor_url,
                                            genius_execution_id = genius_execution_id,
                                            team_handle = team_handle,
                                            
                                            )
                
                result.objects.filter(report_id=report_id).update(
                                                                  title=report_title,
                                                                  url=url,
                                                                  severity_rating=severity_rating,
                                                                 state = state,
                                                                 substate = substate,
                                                                 created_at = created_at,
                                                                 username = username,
                                                                 username_url = username_url,
                                                                 team_name = team_name,
                                                                 team_url = team_url,
                                                                 team_about = team_about,
                                                                 has_bounty = has_bounty,
                                                                 can_view_team = can_view_team,
                                                                 is_external_bug = is_external_bug,
                                                                 is_participant = is_participant,
                                                                 public = public,
                                                                 visibility = visibility,
                                                                 cve_ids = cve_ids,
                                                                 singular_disclosure_disabled = singular_disclosure_disabled,
                                                                 disclosed_at = disclosed_at,
                                                                 bug_reporter_agreed_on_going_public_at =bug_reporter_agreed_on_going_public_at,
                                                                 team_member_agreed_on_going_public_at = team_member_agreed_on_going_public_at,
                                                                 comments_closed = comments_closed,
                                                                 vulnerability_information = vulnerability_information,
                                                                 vulnerability_information_html = vulnerability_information_html,
                                                                 original_report_id = original_report_id,
                                                                 original_report_url = original_report_url,
                                                                 allow_singular_disclosure_at = allow_singular_disclosure_at,
                                                                 allow_singular_disclosure_after = allow_singular_disclosure_after,
                                                                 singular_disclosure_allowed = singular_disclosure_allowed,
                                                                 vote_count = vote_count,
                                                                  )
            else:
                pass
def  scrappe():
    pages = get_page()
    resu(pages)
def update():
    pages =get_page()   #last record page
    summary1= summary.objects.all().last() 
    total_report1 = summary1.total_reports
    summary2 = summary.objects.all().order_by('-pk')[1:2]      #last second record
    for sum2 in summary2:
        page2 = sum2.pages
        total_report2 = sum2.total_reports
        last_time = sum2.create_time
    page = int(pages)-int(page2)
    if page==0:
        page =2
    else:
        page = page +2
    total_report = int(total_report1) - int(total_report2)
    if total_report==0:
        pass
    else:
        resu(page)
