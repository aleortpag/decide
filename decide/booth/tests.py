import datetime
import random
from django.test import TestCase
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.conf import settings
from django.contrib.auth.models import User
from django.utils import timezone

from base.tests import BaseTestCase
import time

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from base import mods

from mixnet.mixcrypt import ElGamal
from mixnet.mixcrypt import MixCrypt

from mixnet.models import Auth
from voting.models import Voting, Question, QuestionOption
from census.models import Census


# Create your tests here.

class BoothTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
    def tearDown(self):
        super().tearDown()
    def testBoothNotFound(self):
        
        # Se va a probar con el numero 10000 pues en las condiciones actuales en las que nos encontramos no parece posible que se genren 10000 votaciones diferentes
        response = self.client.get('/booth/10000/')
        self.assertEqual(response.status_code, 404)
    
    def testBoothRedirection(self):
        
        # Se va a probar con el numero 10000 pues en las condiciones actuales en las que nos encontramos no parece posible que se genren 10000 votaciones diferentes
        response = self.client.get('/booth/10000')
        self.assertEqual(response.status_code, 301)


class StatisticsTestCase(StaticLiveServerTestCase):
    def setUp(self):
        #Opciones de Chrome
        options = webdriver.ChromeOptions()
        options.add_argument('--no-sandbox')
        options.add_argument('--headless')

        # options.headless = True
        self.driver = webdriver.Chrome(options=options)

        super().setUp()            
            
    def tearDown(self):           
        super().tearDown()
        self.driver.quit()

    def create_voting(self):
        q = Question(desc='test question')
        q.save()
        
        for i in range(5):
            opt = QuestionOption(question=q, option='option {}'.format(i+1))
            opt.save()
        v = Voting(name='test voting', question=q, start_date=timezone.now())
        v.save()
        
        a, _ = Auth.objects.get_or_create(url=self.live_server_url,
                                          defaults={'me': True, 'name': 'test auth'})
        a.save()
        v.auths.add(a)

        return v
    
    def create_voter(self, v):
            u, _ = User.objects.get_or_create(username='stats')
            u.is_active = True
            u.set_password('qwerty')
            u.save()
            c = Census(voter_id=u.id, voting_id=v.id)
            c.save()

    def encrypt_msg(self, msg, v, bits=settings.KEYBITS):
        pk = v.pub_key
        p, g, y = (pk.p, pk.g, pk.y)
        k = MixCrypt(bits=bits)
        k.k = ElGamal.construct((p, g, y))
        return k.encrypt(msg)
    

    def test_statistics(self):   
        # Create voting, Question and Auth
        v = self.create_voting()

        # Create voters and add them to Census
        self.create_voter(v)

        # Create pubkey for Voting
        v.create_pubkey()
        v.start_date = timezone.now()
        v.save()
        time.sleep(1)

        # Navigate to booth view
        self.driver.get(f'{self.live_server_url}/booth/{v.id}/')
        print(self.driver.request)
        # Check stats button not visible (not logged already)
        stats = len(self.driver.find_elements(By.ID,'statistics_btn'))==0
        self.assertTrue(stats)

        # Navigate to log in
        self.driver.find_element(By.CLASS_NAME, 'navbar-toggler-icon').click()
        self.driver.implicitly_wait(1)
        self.driver.find_element(By.CLASS_NAME, 'btn-secondary').click()

        # Input credentials to login
        self.driver.find_element(By.ID, 'username').send_keys("stats")
        self.driver.find_element(By.ID, 'password').send_keys("qwerty")
        time.sleep(1)
        self.driver.find_element(By.CLASS_NAME, 'btn-primary').click()

        # Check statistics not shown
        self.assertTrue(len(self.driver.find_elements(By.CLASS_NAME,'statistics')) == 0)

        # Click on statistics button and check statistics shown
        self.driver.find_element(By.ID,'statistics_btn').click()
        self.assertTrue(len(self.driver.find_elements(By.CLASS_NAME,'statistics')) == 1)
