from fasthtml.common import *
from monsterui.all import *
from fastcore.utils import L, Path
import yaml
from datetime import date
from slugify import slugify
from starlette.exceptions import HTTPException
import apsw
import apsw.bestpractice
import json
from datetime import date

github_url = 'https://github.com/nghorvat'
twitter_url = 'https://x.com/DJSnuggz'
linkedin_url = 'https://www.linkedin.com/in/nathan-horvath/'

dark_yellow = '#E4A300'
dark_grey = '#1A1A1A'
light_grey = '#333333'
muted_white = '#BDBDBD'
extra_muted_white = '#8A8780'

def _social_icon_link(platform, h, w):
    urls = {'github': github_url, 'twitter': twitter_url, 'linkedin': linkedin_url}
    return UkIconLink(platform, height=h, width=w, href=urls[platform], cls=f"text-[{dark_yellow}]")

hdrs = (
    Theme.yellow.headers(mode='dark')
)

def _navbar():
    return Div(cls=f'bg-[{dark_grey}]')(
            NavBar(
            DivLAligned(
                A('About', href='/', cls=(TextPresets.bold_lg, f"text-[{dark_yellow}]")),
                A('Blog', href='/blog', cls=(TextPresets.bold_lg, f"text-[{dark_yellow}]")),
                _social_icon_link('github', 24, 24),
                _social_icon_link('twitter', 24, 24),
                _social_icon_link('linkedin', 24, 24),
                cls='space-x-6 mr-4'
            ),
            brand=A(H2('Nathan Horvath', cls=(f'text-[{dark_yellow}] ml-4', TextT.bold)), href="/")
        )
    )

def _error_page(code_str, message_str, gif_path, txt_str):
    return Div(
        _navbar(),
        Container(
            H1(code_str, cls=(f"text-[{dark_yellow}]", 'text-6xl text-center')),
            H1(message_str, cls="text-center"),
            Img(src=gif_path, cls='w-3/4 max-w-screen-sm mx-auto'),
            P(txt_str, cls=(TextT.lg, f"text-[{muted_white}] text-center")),
            Div(
                A(Button("Go Home", cls=(ButtonT.primary, f'bg-[{dark_yellow}]')), href="/"),
                cls="flex justify-center"
            ),
            cls=(ContainerT.lg, 'space-y-6 py-6')
        )
    )

def not_found(req, exc): return _error_page("404", "Page Not Found", "/static/larry-david-lost.gif", "The page you're looking for doesn't exist or has been moved.")
def server_error(req, exc): return _error_page("500", "Server Error", "/static/larry-david-sorry.gif", "Something went wrong on our server. Please try again later.")

app, rt = fast_app(hdrs=hdrs, 
                   live=True, 
                   exception_handlers={404: not_found,
                                       HTTPException: not_found,
                                       Exception: server_error}
                    )

def _post_data(folder_name):
    md_name = folder_name.ls(file_exts=['.md'])[0]
    _, meta, post = md_name.read_text().split('---\n')
    meta = yaml.safe_load(meta)
    meta['image_path'] = folder_name / meta['image']
    meta['slug'] = slugify(meta['title'], replacements=[("'", "")])
    return meta, post

_posts_cache = None

def load_posts():
    global _posts_cache
    if _posts_cache is None:
        _posts_cache = Path('posts').ls().map(_post_data).sorted(key=lambda p: date.fromisoformat(p[0]['date']), reverse=True)
    return _posts_cache

def _blog_card(post):

    def SmallLabel(text): return Label(text, cls=f'bg-[{light_grey}]')
    def SmallTags(cats): return DivLAligned(map(SmallLabel, cats))

    meta = post[0]

    return Card(
        DivLAligned(
            A(Img(src=meta['image_path'], style="width:200px"),href=f'/blog/posts/{meta["slug"]}'),
            Div(cls='space-y-3 w-full')(
                A(H3(meta["title"]), href=f'/blog/posts/{meta["slug"]}'),
                P(meta["description"], cls=f"text-[{muted_white}] text-lg"),
                DivFullySpaced(map(Small, [meta["author"], meta["date"]]), cls=f"text-[{extra_muted_white}]"),
                DivFullySpaced(
                    SmallTags(meta["categories"]),
                    A(Button("Read",  cls=(ButtonT.primary, 'h-6', f'bg-[{dark_yellow}]')), href=f'/blog/posts/{meta["slug"]}')))),
        cls=(CardT.hover, f"bg-[{dark_grey}] rounded-lg"))

def _author_pub_box(meta):
    return Div(
        DivFullySpaced(
            DivLAligned(
                P('AUTHOR', cls=(f"text-[{extra_muted_white}] text-lg", 'mr-4')),
                P(meta['author'], cls=TextT.lg)
            ),
            DivLAligned(
                P('PUBLISHED', cls=(f"text-[{extra_muted_white}] text-lg", 'mr-4')),
                P(meta['date'], cls=TextT.lg)
            ),
            Div(), # dummy Div to force second item to center-ish
            cls='p-6'
        ),
        cls=f'bg-[{dark_grey}] rounded-lg'
    )

    
def _blog_post(meta, content):

    def LargeLabel(text): return Label(text, cls=(TextT.lg, f'bg-[{light_grey}]'))
    def LargeTags(cats): return DivLAligned(map(LargeLabel, cats))

    return Article(
        ArticleTitle(meta['title']),
        P(meta['description'], cls=f"text-[{muted_white}] text-lg"),
        LargeTags(meta['categories']),
        _author_pub_box(meta),
        DividerSplit(),
        render_md(content),
        cls='prose space-y-4'
    )

@rt("/subscribe")
def post(email: str):
    # Here we'll add the email to our database
    # For now, let's just return a confirmation message
    return Div(
        P("Thanks for subscribing!", cls=TextT.bold),
        cls="p-3 rounded-md bg-green-700"
    )

def _subscribe_form(input_width=None):
    input_cls = (TextT.lg, f'bg-[{light_grey}]')
    if input_width:
        input_cls = (*input_cls, input_width)
    return Form(
            DivHStacked(
                Input(placeholder="Your email", name='email', type='email', required=True, cls=input_cls),
                Button("Subscribe", cls=(ButtonT.primary, f'bg-[{dark_yellow}]'))
            ),
            hx_post="/subscribe",
            hx_swap="outerHTML"
    )

def _blog_post_footer():
    return Div(
        DividerSplit(),
        P(I('Thanks for reading!'), cls=(TextT.lg, f'text-[{muted_white}]')),
        Div(
            P("Enjoyed this post?", cls=TextPresets.bold_lg),
            P("Subscribe to get notified when I publish new content", cls=(TextT.lg, f'text-[{muted_white}]')),
            _subscribe_form(input_width='w-80'),
            cls=(f"bg-[{dark_grey}]", "rounded-lg space-y-4 p-4")
        ),
        cls = 'space-y-8'
    )

@rt
def index():
    return Div(
        _navbar(),
        Container(
            H1("About Me", cls="text-center"),
            Img(src="/static/nh-headshot.jpg", cls='rounded-full w-64 h-64 object-cover mx-auto'),
            P("I'm a Data Scientist exploring the intersection of machine learning, operations research, and artificial intelligence to solve real-world challenges.", cls=(TextPresets.bold_lg, "text-center")),
            P("On this blog, I share insights from my learning journey with Python programming, data science concepts, and emerging AI tools.", cls=(TextT.lg, "text-center")),
            P("I'll be gradually expanding this website with new posts and projects.", cls=(TextT.lg, "text-center")),
            Div(
                P("Subscribe to follow along", cls=(TextPresets.bold_lg, "text-center")),
                _subscribe_form(),
                cls=('space-y-4 p-4 mx-auto max-w-md', f"bg-[{dark_grey}]", "rounded-lg")
            ),
            DividerSplit(cls='space-y-4'),
            Div(
                DivHStacked(
                    _social_icon_link('github', 48, 48),
                    _social_icon_link('twitter', 48, 48),
                    _social_icon_link('linkedin', 48, 48),
                    cls='space-x-12 justify-center'
                ),
                cls="flex justify-center"
            ),
            cls=(ContainerT.lg, 'space-y-8 py-6')
        )
    )

    

@rt("/blog")
def blog_home():
    return Div(
        _navbar(),
        Container(
            H1("Some Lessons Learned"),
            DividerSplit(),
            *[_blog_card(post) for post in load_posts()],
            DividerSplit(),
            Div(
                P("Get notified about new posts", cls=TextPresets.bold_lg),
                _subscribe_form(input_width='w-1/4'),
                cls=(f"bg-[{dark_grey}]", "rounded-lg space-y-3 p-4")
            ),
            cls=(ContainerT.lg, 'space-y-8 py-6')
        )
    )

@rt("/blog/posts/{slug}")
def blog_post_page(slug: str):
    all_posts = load_posts()
    idx = first_match(all_posts, lambda p: p[0]['slug'] == slug)
    if idx is None:
        raise HTTPException(status_code=404, detail=f"Blog post with slug '{slug}' not found")
    post = all_posts[idx]
    return Div(
        _navbar(),
        Container(
            _blog_post(*post),
            _blog_post_footer(),
            cls=(ContainerT.lg, 'space-y-6 py-6')
        ),
        
    )


serve()
