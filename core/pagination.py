from rest_framework.pagination import PageNumberPagination

class QuestionPagination(PageNumberPagination):
    page_size = 10  # Number of questions per page
    page_size_query_param = 'page_size'
    max_page_size = 100
