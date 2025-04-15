def is_valid_post(post, min_text_length=50):
    """
    Validate a Reddit post dictionary before processing or storing.
    """

    #    1. Check for required fields in the post
    required_keys = ["id", "title", "selftext", "subreddit"]
    for key in required_keys:
        if key not in post or not post[key]:
            print(f"Missing required field: {key} in post: {post}")
            return False

    #    2. Check if the post is removed or deleted
    text = post["selftext"].strip().lower()
    if text in ["[removed]", "[deleted]", ""]:
        print(f"Skipping removed/deleted/empty post: {post['id']}")
        return False

    #   checks if a post has same title and body
    if post["title"].strip().lower() == post["selftext"].strip().lower():
        print(f"Post title and body are identical, skipping: {post['id']}")
        return False

    return True
