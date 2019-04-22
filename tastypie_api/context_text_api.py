# context_text/tastypie/context_text_api.py
from tastypie.resources import ModelResource
from context_text.models import Article


class ArticleResource( ModelResource ):

    class Meta:

        queryset = Article.objects.all()
        resource_name = 'article'
        
    #-- END Meta class --#
    
#-- END resouce ArticleResource --#