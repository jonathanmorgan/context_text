test_string = "said. \"It's unfortunate,\" Randy Smith said. \"He lived to hunt, and that's what brought us all"

test_article = Article.objects.filter( id = 65897 ) .get()

test_article_text = test_article.article_text_set.get()

test_find = test_article_text.find_in_paragraph_list( test_string )