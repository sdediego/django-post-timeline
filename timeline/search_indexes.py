from haystack import indexes

from .models import Post

# Create your search indexes here.

class PostIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    author = indexes.CharField(model_attr='author')
    title = indexes.CharField(model_attr='title')
    body = indexes.CharField(model_attr='body')
    created = indexes.CharField(model_attr='created')
    last_updated = indexes.CharField(model_attr='last_updated')

    def get_model(self):
        return Post

    def index_queryset(self, using=None):
        "Used when the entire index for model is updated."
        return self.get_model().objects.all()
