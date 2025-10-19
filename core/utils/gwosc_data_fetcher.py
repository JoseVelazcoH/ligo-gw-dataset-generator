import requests
from bs4 import BeautifulSoup
from typing import List

from logger import Logger
class GWOSCDataFetcher:
    def match_gwosc_strain_timelines( ) -> List[str]:
        H1_complete_urls = GWOSCDataFetcher._get_gwosc_strain_urls(detector="H1")
        L1_complete_urls = GWOSCDataFetcher._get_gwosc_strain_urls(detector="L1")
        V1_complete_urls = GWOSCDataFetcher._get_gwosc_strain_urls(detector="V1")

        H1_match_urls = []
        L1_match_urls = []
        V1_match_urls = []
        for timeline in H1_complete_urls:
            if timeline in L1_complete_urls and timeline in V1_complete_urls:
                H1_match_urls.append(V1_complete_urls[timeline])
                L1_match_urls.append(L1_complete_urls[timeline])
                V1_match_urls.append(V1_complete_urls[timeline])

        return H1_match_urls, L1_match_urls, V1_match_urls

    @staticmethod
    def _get_gwosc_strain_urls(
            detector: str = "H1",
            run: str = "O3b_4KHZ_R1"
    ) -> List[str]:
        url = f"https://gwosc.org/archive/links/{run}/{detector}/1256655618/1269363618/simple/"
        Logger.info(f"Fetching GWOSC strain URLs for detector {detector} for run {run}")
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find('table')
        rows = table.find_all('tr')

        links = {}
        for row in rows[1:]:
            columns = row.find_all('td')
            if columns[5].text.strip() == '100.0':
                timeline = columns[0].text.strip()
                link = 'https://gwosc.org' + columns[3].find('a')['href']
                links[timeline] = link
        return links
