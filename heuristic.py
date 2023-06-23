import pdfplumber
import Levenshtein as lev

import numpy as np
from scipy.signal import argrelextrema

def extract_pages(directory: str) -> list[str]:
    pages = []
    with pdfplumber.open(directory) as pdf:
        for page in pdf.pages:
            pages.append(page.extract_text())
    return pages

def standardize(string: str) -> str:
    return string.lower().replace('\n', ' ').replace('  ', ' ')

def find_local_minima_with_plateau(arr, plateau_threshold=0.0):
    minima = []
    n = len(arr)

    for i in range(1, n-1):
        if arr[i] <= arr[i-1] and arr[i] <= arr[i+1]:
            if np.allclose(arr[i], arr[i-1], atol=plateau_threshold) or np.allclose(arr[i], arr[i+1], atol=plateau_threshold):
                minima.append(i)
            elif arr[i] < np.min([arr[i-1], arr[i+1]]):
                minima.append(i)

    return np.array(minima)

def fuzzy_find(text: str, value: str, max_dist: int = 10) -> list[int]:
    len_str = len(value)
    text_std = standardize(text)
    value_std = standardize(value)

    distances = []
    for i in range(1, len(text_std)-len(value_std)):
        distances.append(lev.distance(text_std[i: i+len(value_std)], value_std))
    
    distances = np.array(distances)
    minima_indecies = find_local_minima_with_plateau(distances)
    if (len(minima_indecies) == 0): return []
    filter = distances[minima_indecies] < max_dist
    
    ans = []
    last = -1
    for elem_pos in minima_indecies[filter]:
        if last!=-1 and last+len_str > elem_pos:
            pass
        else:
            ans.append(elem_pos)
            last=elem_pos
    return ans# minima_indecies[filter]

if __name__ == "__main__":
  pages = extract_pages(directory)
  title = 'Капитальный ремонт автомобильной дороги Р-215 Астрахань - Кочубей - Кизляр - Махачкала, подъезд к г. Грозный на участке км 70+127 - км 85+267, Чеченская Республика'

  for page_num, page in enumerate(pages):
      match_starts = fuzzy_find(page, title)
      if(len(match_starts) != 0):
          print([f"Found title on page {page_num:3} char {start:4} {page[start: start+len(title)]}"
                      for start in match_starts])
