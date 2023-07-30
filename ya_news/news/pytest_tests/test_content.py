import pytest
from django.urls import reverse
from news.models import News


@pytest.mark.django_db
def test_news_order_and_count(client):
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    print(object_list.count)
    assert all_dates == sorted_dates
    assert len(object_list) <= 10


@pytest.mark.django_db
def test_comments_order(client, comment_data):
    news = News.objects.first()
    detail_url = reverse('news:detail', args=[news.id])
    response = client.get(detail_url)
    news = response.context['news']
    all_comments = news.comment_set.all()
    assert all_comments[0].created < all_comments[1].created


@pytest.mark.django_db
def test_anonymous_client_has_no_form(client, comment_data):
    news = News.objects.first()
    detail_url = reverse('news:detail', args=[news.id])
    response = client.get(detail_url)
    assert 'form' not in response.context


@pytest.mark.django_db
def test_authorized_client_has_form(author_client, comment_data):
    news = News.objects.first()
    detail_url = reverse('news:detail', args=[news.id])
    response = author_client.get(detail_url)
    assert 'form' in response.context
