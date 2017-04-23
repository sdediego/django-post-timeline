# Copyright (c) 2016 Publisher, Inc. - All Rights Reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.
# Proprietary and confidential.
# Written by Sergio de Diego <sergio.dediego@outlook.com>, October 2016.

import re

from django import template
from django.template.defaultfilters import stringfilter

# Create your template filters here.

register = template.Library()

@register.filter(name='video_url')
@stringfilter
def video_url(url):
    regex = re.compile(r'^((http|https)://)?(www\.)?(?P<host>youtube\.com/watch\?v=)?(?P<id>[A-Za-z0-9\-=_]+)')
    match = regex.match(url)
    video_id = match.group('id')
    if video_id != None:
        #html_tag = '<iframe width="560" height="315" src="{video_id}" frameborder="0" allowfullscreen></iframe>'.format(video_id=video_id)
        html_tag = """
        <object width="425" height="344">
        <param name="movie" value="http://www.youtube.com/watch/v/%s"></param>
        <param name="allowFullScreen" value="true"></param>
        <embed src="http://www.youtube.com/watch/v/%s" type="application/x-shockwave-flash" allowfullscreen="true" width="425" height="344"></embed>
        </object>
        """ % (video_id, video_id)
        return html_tag  # incluir en el html {{ link.url|video_url|safe }}
    else:
        return None
