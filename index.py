import elasticsearch

mapping = {
    "mappings": {
        # "_doc": {
        "properties": {
            "country": {"type": "text"},
            "country_code": {"type": "text"},
            "name": {"type": "text"},
            "full_name": {"type": "text"},
            "place": {
                "properties":
                    {
                        # "bounding_box": {"type": "geo_point"},
                        "point": {"type": "geo_point"},
                    },
            },
            "text": {
                "type": "text",
                    "analyzer": "kuromoji",
                    "fielddata": True,
                    "fields": {
                        "keyword": {
                            "type": "keyword", "ignore_above": 256
                        }
                    }
            }
        }
        #   }
    },
    "settings": {
        "analysis": {
            "analyzer": {
                "kuromoji": {
                    "type": "custom",
                    "tokenizer": "kuromoji_tokenizer"
                }
            }
        }
    }
}
client = elasticsearch.Elasticsearch("localhost:9200")
client.indices.create(index='twitter', body=mapping)
