from functools import partial
from django import template
from django.template.base import TagHelperNode, token_kwargs
from django.template.defaultfilters import safe

register = template.Library()


class EmailContentTransform(TagHelperNode):
    def __init__(self, tag_name, parser, token):
        self.tag_name = tag_name

        bits = token.split_contents()[1:]
        self.kwargs = {k: v.var for k,v in token_kwargs(bits, parser).items()}

        nodelist = parser.parse(('end{0}'.format(tag_name),))
        parser.delete_first_token()
        self.nodelist = nodelist

    def render(self, context):
        email_template_namespace = context.get("alert_shardtype", "default")
        shard_ext = context.get("alert_shard_ext", "txt")

        template_file = "alerts/email_shards/{0}/{1}.{2}".format(
            email_template_namespace,
            self.tag_name,
            shard_ext
        )

        t = context.template.engine.get_template(template_file)

        content = self.nodelist.render(context)

        with context.push(content=content, **self.kwargs):
            rendered = t.render(context)

            if shard_ext == "html":
                rendered = safe(rendered.replace("\n", "<br>"))

            return rendered


email_tags = [
    "a", "p", "h1", "h2"
]
for tag_name in email_tags:
    fn = partial(EmailContentTransform, tag_name)
    register.tag(name=tag_name)(fn)


class EmailShardTypeNode(template.Node):
    def __init__(self, shard_type, nodelist):
        self.shard_type = shard_type
        self.nodelist = nodelist

    def render(self, context):
        with context.push(alert_shardtype=self.shard_type):
            return self.nodelist.render(context)


@register.tag
def shardtype(parser, token):
    try:
        # split_contents() knows not to split quoted strings.
        tag_name, shard_type = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError(
            "%r tag requires a single argument" % token.contents.split()[0]
        )
    if not (shard_type[0] == shard_type[-1] and shard_type[0] in ('"', "'")):
        raise template.TemplateSyntaxError(
            "%r tag's argument should be in quotes" % tag_name
        )

    shard_type = shard_type[1:-1]
    nodelist = parser.parse(('end{0}'.format(tag_name),))
    parser.delete_first_token()

    return EmailShardTypeNode(shard_type, nodelist)