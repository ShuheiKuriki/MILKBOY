from django.db import models
class Scripts(models.Model):
    """
    ネタモデル
    """
    input_theme = models.CharField('input_theme', max_length=32)
    theme = models.CharField('theme', max_length=32)
    stage = models.IntegerField('stage', choices=[(i, i) for i in range(7)], default=4)
    seed = models.IntegerField('seed', default=-1)
    category = models.CharField('category', max_length=32)
    anti_theme = models.CharField('anti_theme', max_length=32)
    featX = models.CharField('featX', max_length=256)
    featX_reply = models.CharField('featX_reply', max_length=256)
    anti_featX = models.CharField('anti_featX', max_length=256)
    anti_featX_reply = models.CharField('anti_featX_reply', max_length=256)
    conjunction = models.CharField('conjunction', max_length=256)
    next_is_last = models.BooleanField("next_is_last", default=False)


    def todict(self):
        return {
            "input_theme": self.input_theme,
            "theme": self.theme,
            "stage": self.stage,
            "seed": self.seed,
            "category": self.category,
            "anti_theme": self.anti_theme,
            "featX": self.featX,
            "featX_reply": self.featX_reply,
            "anti_featX": self.featX,
            "anti_featX_reply": self.featX_reply,
            "conjunction": self.conjunction,
            "next_is_last": self.next_is_last,
        }

# Create your models here.
