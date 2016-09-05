import requests,bs4,re,sqlite3,os,scraperwiki

def extract_details(soup,house):
  db = sqlite3.connect('data.sqlite')
  qry = db.cursor()
  results = soup.find('div',class_='search-filter-results').find_all('div',class_='row')
  for r in results:
    row = {}
    title = r.find('h4',class_='title').a
    row['mpid']=re.search('.*MPID=(.*)$',title['href']).groups()[0]
    row['fullname']=title.text
    row['house']=house
    row['party']=r.find('dl').find('dt',text='Party').next_sibling.next_sibling.text
    row['electorate']=r.find('dl').find('dt',text='For').next_sibling.next_sibling.text
    row['profile_page']=r.find('p',class_='result__thumbnail_parl').a['href']
    row['contact_page']='http://www.aph.gov.au/Senators_and_Members/Contact_Senator_or_Member?MPID='+row['mpid']
    row['image_url']=r.find('p',class_='result__thumbnail_parl').img.get('src') if r.find('p',class_='result__thumbnail_parl').img else ''
    prof = bs4.BeautifulSoup(requests.get('http://www.aph.gov.au'+row['profile_page']).content,'lxml')
    connect = prof.find('div',id='panel31')
    row['email']=connect.find('a',href=re.compile('^mailto:'))['href'][7:] if connect.find('a',href=re.compile('^mailto:')) else ''
    row['facebook']=connect.find('a',title='Facebook')['href'] if connect.find('a',title='Facebook') else ''
    row['twitter']=connect.find('a',title='Twitter')['href'] if connect.find('a',title='Twitter') else ''
    row['website']=connect.find(text='Personal website').parent['href'] if connect.find(text='Personal website') else ''
    print '  ',row['fullname']
    scraperwiki.sqlite.save(unique_keys=['mpid'], data=row)

base_url = 'http://www.aph.gov.au/Senators_and_Members/Parliamentarian_Search_Results'

# members
pgnum = 1
pg = requests.get(base_url+'?mem=1&q=')
soup = bs4.BeautifulSoup(pg.content,'lxml')
next_link = soup.find('a',text='Next')
while next_link:
  print 'parsing members page',pgnum
  extract_details(soup,'Reps')      
  next_link = soup.find('a',text='Next')
  if next_link:
    pg = requests.get(base_url+next_link['href'])
    soup = bs4.BeautifulSoup(pg.content,'lxml')
    pgnum += 1 
  
# senators
pgnum = 1
pg = requests.get(base_url+'?sen=1&q=')
soup = bs4.BeautifulSoup(pg.content,'lxml')
next_link = soup.find('a',text='Next')
while next_link:
  print 'parsing senators page',pgnum
  extract_details(soup,'Senate')      
  next_link = soup.find('a',text='Next')
  if next_link:
    pg = requests.get(base_url+next_link['href'])
    soup = bs4.BeautifulSoup(pg.content,'lxml')
    pgnum += 1 
