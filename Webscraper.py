import pandas as pd
from bs4 import BeautifulSoup
from selenium.webdriver import Chrome
import re
import time
import json
import math

headers = {
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'}
path = "/Users/peiming/Downloads/chromedriver-2"
driver = Chrome(executable_path=path)
time.sleep(2)
base_url = "https://www.jobstreet.com.sg/en/job-search/{}-jobs/{}/"


def get_page_number(keyword):
    # input: keyword for job_postings
    # output: number of pages

    url = base_url.format(keyword, 1)
    driver.get(url)
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    #result_text = soup.find("span", {"class": "sx2jih0 zcydq84u _18qlyvc0 _18qlyvc1x _18qlyvc1 _1d0g9qk4 _18qlyvc8"})
    result_text = soup.find('span',{'class': "sx2jih0 zcydq84u es8sxo0 es8sxo1 es8sxo21 _1d0g9qk4 es8sxo7"})
    results = result_text.text.split()
    result = result_text.text.split()[-2]
    result = result.replace(',', '')
    page_number = math.ceil(int(result) / 30)

    return page_number


def job_page_scraper(link):
    url = "https://www.jobstreet.com.sg" + link
    print("scraping...", url)
    driver.get(url)
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    scripts = soup.find_all("script")

    for script in scripts:
        if script.contents:
            txt = script.contents[0].strip()
            if 'window.REDUX_STATE = ' in txt:
                jsonStr = script.contents[0].strip()
                jsonStr = jsonStr.split('window.REDUX_STATE = ')[1].strip()
                jsonStr = jsonStr.split('}}}};')[0].strip()
                jsonStr = jsonStr + "}}}}"
                jsonObj = json.loads(jsonStr)

    job = jsonObj['details']
    job_id = job['id']
    job_expired = job['isExpired']
    job_confidential = job['isConfidential']
    job_salary_min = job['header']['salary']['min']
    job_salary_max = job['header']['salary']['max']
    job_salary_currency = job['header']['salary']['currency']
    job_title = job['header']['jobTitle']
    company = job['header']['company']['name']
    job_post_date = job['header']['postedDate']
    job_internship = job['header']['isInternship']
    company_website = job['companyDetail']['companyWebsite']
    company_avgProcessTime = job['companyDetail']['companySnapshot']['avgProcessTime']
    company_registrationNo = job['companyDetail']['companySnapshot']['registrationNo']
    company_workingHours = job['companyDetail']['companySnapshot']['workingHours']
    company_facebook = job['companyDetail']['companySnapshot']['facebook']
    company_size = job['companyDetail']['companySnapshot']['size']
    company_dressCode = job['companyDetail']['companySnapshot']['dressCode']
    company_nearbyLocations = job['companyDetail']['companySnapshot']['nearbyLocations']
    company_overview = job['companyDetail']['companyOverview']['html']
    job_description = job['jobDetail']['jobDescription']['html']
    job_summary = job['jobDetail']['summary']
    job_requirement_career_level = job['jobDetail']['jobRequirement']['careerLevel']
    job_requirement_yearsOfExperience = job['jobDetail']['jobRequirement']['yearsOfExperience']
    job_requirement_qualification = job['jobDetail']['jobRequirement']['qualification']
    job_requirement_fieldOfStudy = job['jobDetail']['jobRequirement']['fieldOfStudy']
    # job_requirement_industry = job['jobDetail']['jobRequirement']['industryValue']['label']
    job_requirement_skill = job['jobDetail']['jobRequirement']['skills']
    job_employment_type = job['jobDetail']['jobRequirement']['employmentType']
    job_languages = job['jobDetail']['jobRequirement']['languages']
    job_benefits = job['jobDetail']['jobRequirement']['benefits']
    job_apply_url = job['applyUrl']['url']
    job_location_zipcode = job['location'][0]['locationId']
    job_location = job['location'][0]['location']
    job_country = job['sourceCountry']

    return [job_id, job_title, job_expired, job_confidential, job_salary_max, job_salary_max, job_salary_currency,
            company, job_post_date, job_internship, company_website, company_avgProcessTime, company_registrationNo,
            company_workingHours, company_facebook, company_size, company_dressCode, company_nearbyLocations,
            company_overview, job_description, job_summary, job_requirement_career_level, job_requirement_fieldOfStudy,
            job_requirement_yearsOfExperience, job_requirement_qualification, job_requirement_skill,
            job_employment_type, job_languages, job_benefits, job_apply_url, job_location_zipcode, job_location,
            job_country]


def page_crawler(keyword):
    # input: keyword for job postings
    # output: dataframe of links scraped from each page

    # page number
    page_number = get_page_number(keyword)
    job_links = []

    for n in range(71):
        print('Loading page {} ...'.format(n))
        url = base_url.format(keyword, n)
        driver.get(url)
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # extract all job links
        links = soup.find_all('a', {'class' :"_1hr6tkx5 _1hr6tkx7 _1hr6tkxa sx2jih0 sx2jihf zcydq8h"})
        job_links += links

    jobs = []

    for link in job_links:
        job_link = link['href'].strip().split('?', 1)[0]
        if "job-search" not in job_link:
            jobs.append([keyword, job_link] + job_page_scraper(job_link))

    print(jobs)

    result_df = pd.DataFrame(jobs, columns=['keyword', 'link', 'job_id', 'job_title', 'job_expired', 'job_confidential',
                                            'job_salary_max', 'job_salary_max', 'job_salary_currency', 'company',
                                            'job_post_date', 'job_internship', 'company_website',
                                            'company_avgProcessTime', 'company_registrationNo', 'company_workingHours',
                                            'company_facebook', 'company_size', 'company_dressCode',
                                            'company_nearbyLocations', 'company_overview', 'job_description',
                                            'job_summary', 'job_requirement_career_level',
                                            'job_requirement_fieldOfStudy', 'job_requirement_yearsOfExperience',
                                            'job_requirement_qualification', 'job_requirement_skill',
                                            'job_employment_type', 'job_languages', 'job_benefits', 'job_apply_url',
                                            'job_location_zipcode', 'job_location', 'job_country'])
    return result_df


def main():
    # a list of job roles to be crawled
    key_words = ['"devops"']
    dfs = []

    for key in key_words:
        key_df = page_crawler(key)
        dfs.append(key_df)

    # save scraped information as csv
    pd.concat(dfs).to_csv("devops_71.csv")


if __name__ == '__main__':
    main()

