import scrapy
from scrapy import FormRequest

from scrapy.loader import ItemLoader

from ..items import LfblyItem
from itemloaders.processors import TakeFirst


class LfblySpider(scrapy.Spider):
	name = 'lfbly'
	start_urls = ['https://www.lfb.ly/News_List.aspx']

	def parse(self, response):
		post_links = response.xpath('//div[@class="LatestNewsListTitle"]/a/@href').getall()
		yield from response.follow_all(post_links, self.parse_post)

		next_page = response.xpath('//a[text()="›"]/@href').getall()
		print(next_page)
		if next_page:
			yield FormRequest.from_response(response, formdata={
				'__EVENTTARGET': 'ctl00$ContentPlaceHolder3$pager$ctl03$ctl00'}, callback=self.parse)

	def parse_post(self, response):
		title = response.xpath('//h1/span[@class="Event_Title_Class"]/text()').get()
		description = response.xpath('//div[@class="LatestNewsEventBody"]//text()[normalize-space()]').getall()
		description = [p.strip() for p in description if '{' not in p]
		description = ' '.join(description).strip()
		date = response.xpath('//div[@class="LatestNewsEventPubDate"]/span/text()').get()

		item = ItemLoader(item=LfblyItem(), response=response)
		item.default_output_processor = TakeFirst()
		item.add_value('title', title)
		item.add_value('description', description)
		item.add_value('date', date)

		return item.load_item()
