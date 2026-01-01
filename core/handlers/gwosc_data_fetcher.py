import requests
from bs4 import BeautifulSoup
from typing import List

from core.utils.logger import Logger
from core.utils.source_sampling import get_sources_per_sample
class GWOSCDataFetcher:
    def match_gwosc_strain_timelines(n_samples: int) -> List[str]:
        H1_complete_urls = GWOSCDataFetcher._get_gwosc_strain_urls(detector="H1", run="O3b_4KHZ_R1")
        L1_complete_urls = GWOSCDataFetcher._get_gwosc_strain_urls(detector="L1", run="O3b_4KHZ_R1")
        V1_complete_urls = GWOSCDataFetcher._get_gwosc_strain_urls(detector="V1", run="O3b_4KHZ_R1")
        common_timelines = set(H1_complete_urls.keys()) & set(L1_complete_urls.keys()) & set(V1_complete_urls.keys())

        H1_match_urls = []
        L1_match_urls = []
        V1_match_urls = []

        n_sources = get_sources_per_sample(n_samples=n_samples)
        n_sources_collected = 0

        for timeline in common_timelines:
            H1_match_urls.append(H1_complete_urls[timeline])
            L1_match_urls.append(L1_complete_urls[timeline])
            V1_match_urls.append(V1_complete_urls[timeline])
            n_sources_collected += 1
            if n_sources_collected >= n_sources:
                break
        Logger.info(f"Sources matched collected: {n_sources_collected}", verbose=False)
        urls = {
            "H1": H1_match_urls,
            "L1": L1_match_urls,
            "V1": V1_match_urls
        }
        return urls

    @staticmethod
    def _get_gwosc_strain_urls(
            detector: str,
            run: str
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
