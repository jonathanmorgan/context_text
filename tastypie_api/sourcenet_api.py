# sourcenet/tastypie/sourcenet_api.py
from tastypie.resources import ModelResource
from sourcenet.models import Article


class ArticleResource( ModelResource ):

    class Meta:

        queryset = Article.objects.all()
        resource_name = 'article'
        
    #-- END Meta class --#
    
#-- END resouce ArticleResource --#