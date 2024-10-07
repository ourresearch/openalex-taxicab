from openalex_taxicab.harvest import PublisherLandingPageHarvester
from openalex_taxicab.s3_util import make_s3

s3 = make_s3()

harvester = PublisherLandingPageHarvester(s3)
response = harvester.harvest('10.3389/fnins.2021.765850', 'Frontiers Media SA')
print(response)