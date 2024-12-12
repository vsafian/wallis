from django.http import HttpResponseRedirect, Http404
from django.views import generic


class DeleteViewMixin(generic.DeleteView):
    """
    DeleteViewMixin:
    - Used to handle model deletion with support for the “Cancel” and “Yes” buttons.
    - “Cancel” redirects to the model URL.
    """
    def post(self, request, *args, **kwargs):
        if "cancel" in request.POST:
            obj = self.get_object()
            if not hasattr(obj, 'get_absolute_url'):
                raise Http404(
                    "Object does not have an absolute URL!"
                )
            return HttpResponseRedirect(obj.get_absolute_url())
        else:
            return super().post(request, *args, **kwargs)
