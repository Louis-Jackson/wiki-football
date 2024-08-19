from Search import Search
from DetailSpider import DetailSpider
import argparse

def main(kwargs):
     for key, value in kwargs.items():
          if kwargs['keyword1'] == 'detail':
               detailspider = DetailSpider()
               detailspider.run(kwargs.get('keyword2'))
          else:
               search = Search()
               search.run(kwargs.get('keyword2'))
     

    

if __name__ == '__main__':
     parser = argparse.ArgumentParser(description='Run the search with optional parameters.')
     parser.add_argument('--keyword1', type=str, required=True, help='The keyword parameter (search or detail).')
     parser.add_argument('--keyword2', type=str, required=False, help='The keyword parameter (player, referee, team, venue) or (infobox, image, content).')
     args = parser.parse_args()
     kwargs = vars(args)
     
     main(kwargs)