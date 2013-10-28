'''
Created on Jan 29, 2011

@author: Caleb Kniffen
'''
from django.views.generic.base import View
from django.http import HttpResponse


class DownloadView(View):
    '''
    Generic class view to abstract out the task of serving up files from within Django.
    Recommended usage is to combine it with SingleObjectMixin and extend certain
    methods based on your particular use case.

    Example usage::

        class Snippet(models.Model):
            name = models.CharField(max_length = 100)
            slug = SlugField()
            code = models.TextField()

        from django.views.generic.detail import SingleObjectMixin

        class DownloadSnippetView(SingleObjectMixin, DownloadView):
            model = Snippet
            use_xsendfile = False
            mimetype = 'application/python'

           def get_contents(self):
                return self.get_object().code

            def get_filename(self):
                return self.get_object().slug + '.py'
    '''

    mimetype = None
    extension = None
    filename = None
    use_xsendfile = True

    def get_filename(self):
        return self.filename

    def get_extension(self):
        return self.extension

    def get_mimetype(self):
        return self.mimetype

    def get_location(self):
        ''' Returns the path the file is currently located at.
            Used only if use_xsendfile is True '''
        pass

    def get_contents(self):
        ''' Returns the contents of the file download.  Used only if use_xsendfile is False '''
        pass

    def get(self, request, *args, **kwargs):
        response = HttpResponse(mimetype=self.get_mimetype())
        response['Content-Disposition'] = 'filename=' + self.get_filename()

        if self.use_xsendfile is True:
            response['X-Sendfile'] = self.get_location()
        else:
            response.write(self.get_contents())

        return response
