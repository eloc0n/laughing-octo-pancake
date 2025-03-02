from rest_framework.pagination import PageNumberPagination


class PageNumberPagination(PageNumberPagination):
    """
    A simple page number based style pagination for Plant listings.
    It supports page numbers as query parameters (e.x. ?page=4)
    with the option to define a specific page size (e.x. ?page_size=75).
    """

    page_size = 50
    page_size_query_param = "page_size"
    max_page_size = 100
