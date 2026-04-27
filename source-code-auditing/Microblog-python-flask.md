
[Microblog](https://github.com/miguelgrinberg/microblog)


#### app > main > routes.py

```pythono
@bp.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now(timezone.utc)
        db.session.commit()
        g.search_form = SearchForm()
    g.locale = str(get_locale())
    
```

here bp is blueprint which is handeing the all request, If user is logged in, update their last_seen timestamp and commit to their db.
Attached a search from and locale to the global g object so all the template can use them. 

---

###### index route 

``` python
@bp.route('/', methods=['GET', 'POST'])          # Entry: URL / or /index, allows GET and POST
@bp.route('/index', methods=['GET', 'POST'])
@login_required                                    # User must be logged in
def index():
    form = PostForm()                              # Step 0: Create a form object (Flask-WTF)
    if form.validate_on_submit():                  # Step 1: Did user submit the form? (POST)
        try:
            language = detect(form.post.data)      # Step 2: user input -> form.post.data (text)
        except LangDetectException:
            language = ''                          # 2a: if language detection fails, set to empty
        post = Post(body=form.post.data, author=current_user,
                    language=language)             # Step 3: user input saved into Post object
        db.session.add(post)                       # Step 4: Add to database (sink)
        db.session.commit()                        # Step 4: Actually write to DB
        flash(_('Your post is now live!'))         # Step 5: Flash a success message (output)
        return redirect(url_for('main.index'))     # Step 5: Redirect back to index (output)
    page = request.args.get('page', 1, type=int)   # If GET (normal page load), get ?page= from URL
    posts = db.paginate(current_user.following_posts(), page=page,
                        per_page=current_app.config['POSTS_PER_PAGE'],
                        error_out=False)           # Get posts for current page from DB
    next_url = url_for('main.index', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('main.index', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('index.html', title=_('Home'), form=form,
                           posts=posts.items, next_url=next_url,
                           prev_url=prev_url)      # Output: HTML page
```

- User visit / or /index. their browser sends wither a GET (just load the page ) or POST (they have submitted the new  post form).
- The post body is inside `form.post.data` (which comes from `request.form`). The `page` number comes from the URL query string like `?page=2`.
- The post body goes into a `Post` object and is **saved to the database**. The page number just controls which posts to fetch.
-  **Sanitization/Validation**: Flask-WTF protects against CSRF automatically. The form itself has validators (defined in `app/main/forms.py`) — likely a length check. The body is not HTML-escaped here, but when displayed in the template, Jinja2 will escape it to prevent XSS. Language detection is a non-security feature.
-  output : Either a redirect (after post) or an HTML page with a list of posts.


- `explore`  shows all post from all users 
- no user input needed only `?page=` to page through 
	- reads page from url, then queries in the database for all posts order by time.
	- returns html
	