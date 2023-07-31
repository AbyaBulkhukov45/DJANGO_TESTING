import pytest

from news.models import News
from news.forms import CommentForm


@pytest.mark.django_db
def test_news_order_and_count(client, urls):
    response = client.get(urls['home'])
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.django_db
def test_comments_order(client, comment_data, urls):
    news = News.objects.first()
    response = client.get(urls['detail'])
    news = response.context['news']
    all_comments = news.comment_set.all()
    assert len(all_comments) >= 2
    for i in range(len(all_comments) - 1):
        assert all_comments[i].created < all_comments[i + 1].created


@pytest.mark.django_db
def test_anonymous_client_has_no_form(client, comment_data, urls):
    response = client.get(urls['detail'])
    assert 'form' not in response.context


@pytest.mark.django_db
def test_authorized_client_has_form(author_client, comment_data, urls):
    response = author_client.get(urls['detail'])
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)
