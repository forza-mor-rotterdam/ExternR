from django.db import connections
from prometheus_client.core import CounterMetricFamily


class CustomCollector(object):
    def __init__(self):
        ...

    def dictfetchall(self, cursor):
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def collect(self):
        yield self.collect_celery_task_results()

    def collect_celery_task_results(self):
        c = CounterMetricFamily(
            "morcore_celery_task_results_issues_total",
            "Aantallen van Celery TaskResult instanties per task_name en status, met status FAILED of RETRY",
            labels=[
                "task_name",
                "status",
            ],
        )
        total_objects = []

        sql = '\
            SELECT \
                "django_celery_results_taskresult"."task_name", \
                "django_celery_results_taskresult"."status", \
                COUNT("django_celery_results_taskresult"."task_id") AS "count" \
            FROM "django_celery_results_taskresult" \
            WHERE \
                "django_celery_results_taskresult"."status" IN (\'FAILURE\', \'RETRY\') \
                AND "django_celery_results_taskresult"."task_name" IS NOT NULL \
            GROUP BY \
                "django_celery_results_taskresult"."status", \
                "django_celery_results_taskresult"."task_name" \
            ORDER BY \
                "django_celery_results_taskresult"."status", \
                "django_celery_results_taskresult"."task_name" ASC;\
        '

        with connections["default"].cursor() as cursor:
            cursor.execute(sql)
            total_objects = self.dictfetchall(cursor)

        for obj in total_objects:
            c.add_metric(
                (
                    obj["task_name"],
                    obj["status"],
                ),
                obj["count"],
            )

        return c
