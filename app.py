from fasthtml.common import *
from monsterui.all import *
from fastcore.utils import L, Path
import yaml
from datetime import date
from slugify import slugify
from starlette.exceptions import HTTPException

github_url = 'https://github.com/nghorvat'
twitter_url = 'https://x.com/DJSnuggz'
linkedin_url = 'https://www.linkedin.com/in/nathan-horvath/'

dark_yellow = '#E4A300'
dark_grey = '#1A1A1A'
light_grey = '#333333'
muted_white = '#BDBDBD'
extra_muted_white = '#8A8780'

def _github_icon_link(h, w): return UkIconLink("github", height=h, width=w, href=github_url, cls=f"text-[{dark_yellow}]")
def _twitter_icon_link(h, w): return UkIconLink("twitter", height=h, width=w, href=twitter_url, cls=f"text-[{dark_yellow}]")
def _linkedin_icon_link(h, w): return UkIconLink("linkedin", height=h, width=w, href=linkedin_url, cls=f"text-[{dark_yellow}]")

hdrs = (
    Theme.yellow.headers(mode='dark')
)

def _navbar():
    return Div(cls=f'bg-[{dark_grey}] w-screen')(
            NavBar(
            DivLAligned(
                A('About', href='/', cls=(TextPresets.bold_lg, f"text-[{dark_yellow}]")),
                A('Blog', href='/blog', cls=(TextPresets.bold_lg, f"text-[{dark_yellow}]")),
                _github_icon_link(24, 24),
                _twitter_icon_link(24, 24),
                _linkedin_icon_link(24, 24),
                cls='space-x-6 mr-11'
            ),
            brand=A(H2('Nathan Horvath', cls=(f'text-[{dark_yellow}] ml-11', TextT.bold)), href="/")
        )
    )

def _error_page(code_str, message_str, gif_path, txt_str):
    return Div(
        _navbar(),
        DivCentered(cls='space-y-6 mt-12')(
            H1(code_str, cls=(f"text-[{dark_yellow}]", 'text-6xl')),
            H1(message_str),
            Img(src=gif_path, cls='w-3/4 max-w-screen-sm'),
            P(txt_str, cls=f"text-[{muted_white}] text-lg"),
            A(Button("Go Home", cls=(ButtonT.primary, f'bg-[{dark_yellow}]')), href="/")
        ))

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

posts = Path('posts').ls().map(_post_data).sorted(key=lambda p: date.fromisoformat(p[0]['date']), reverse=True)

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
    return Container(
        DivFullySpaced(
            DivLAligned(
                P('AUTHOR', cls=(f"text-[{extra_muted_white}] text-lg", 'mr-4', '-ml-10')),
                P(meta['author'], cls=TextT.lg)
            ),
            DivLAligned(
                P('PUBLISHED', cls=(f"text-[{extra_muted_white}] text-lg", 'mr-4')),
                P(meta['date'], cls=TextT.lg)
            ),
            Div(),
            cls='p-6'
        ),
        cls=(ContainerT.lg, f'bg-[{dark_grey}] rounded-lg')  # rounded corners on gray box
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

def _subscribe_form():
    return DivHStacked(
        Input(placeholder="Your email", cls=(TextT.lg, f'bg-[{light_grey}]')),
        Button("Subscribe", cls=(ButtonT.primary, f'bg-[{dark_yellow}]'))
    )
           

def _blog_post_footer():
    return Div(
        DividerSplit(),
        P(I('Thanks for reading!'), cls=(TextT.lg, f'text-[{muted_white}]')),
        Container(
            Div(
                P("Enjoyed this post?", cls=TextPresets.bold_lg),
                P("Subscribe to get notified when I publish new content", cls=(TextT.lg, f'text-[{muted_white}]')),
                _subscribe_form(),
                cls='flex flex-col items-start space-y-4 p-4 -ml-2'
            ),
            cls=(ContainerT.lg, "rounded-lg"),
            style=f"background-color: {dark_grey}"
        ),
        cls = 'space-y-6'
    )



@rt("/blog")
def blog_home():
    return Div(
        _navbar(),
        Container(
            Div(
                H1("Some Lessons Learned"),
                DividerSplit(),
                *[_blog_card(post) for post in posts],
                cls='space-y-8 p-6'
            )
        )
    )

@rt
def index():
    return Div(
        _navbar(),
        Container(
            DivCentered(
                H1("About Me"),
                Img(src="/static/nh-headshot.jpg", cls='rounded-full w-64 h-64 object-cover'),
                P("I'm a Data Scientist exploring the intersection of machine learning, operations research, and artificial intelligence to solve real-world challenges.", cls=(TextT.lg, TextT.bold)),
                P("On this blog, I share insights from my learning journey with Python programming, data science concepts, and emerging AI tools.", cls=TextT.lg),
                P("I'll be gradually expanding this website with new posts and projects.", cls=TextT.lg),
                Container(
                        DivCentered(
                            P("Subscribe to follow along", cls=TextPresets.bold_lg),
                            _subscribe_form(),
                            cls='space-y-4 p-4'
                    ),
                    cls=(ContainerT.lg, "rounded-lg"),
                    style=f"background-color: {dark_grey}"
                ),
                cls='space-y-3 p-6'
            ),
            DividerSplit(),
            DivCentered(
                 DivHStacked(
                    _github_icon_link(48, 48),
                    _twitter_icon_link(48, 48),
                    _linkedin_icon_link(48, 48),
                    cls='space-x-12 p-4'
                 )
            )
        )
    )

@rt("/blog/posts/{slug}")
def blog_post_page(slug: str):
    idx = first_match(posts, lambda p: p[0]['slug'] == slug)
    if idx is None:
        raise HTTPException(status_code=404, detail=f"Blog post with slug '{slug}' not found")
    post = posts[idx]
    return Div(
        _navbar(),
        Div(
            _blog_post(*post),
            _blog_post_footer(),
            cls='p-14'
        ),
        
    )



serve()
