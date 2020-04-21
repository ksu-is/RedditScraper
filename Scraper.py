from os.path import isfile
import os
import praw
import pandas as pd
from time import sleep
import datetime as dt
import urllib.request
from tkinter import *

reddit = praw.Reddit("credentials")

class SubredditScraper:
    
    def __init__(self, sub, sort, lim, mode):
        self.sub = sub
        self.sort = sort
        self.lim = lim
        self.mode = mode

        print(f'SubredditScraper instance created with values sub = {sub}, sort = {sort}, lim = {lim}, mode= {mode}')
    
    def set_sort(self):
        if self.sort == 'new':
            return self.sort, reddit.subreddit(self.sub).new(limit=self.lim)
        elif self.sort == 'top':
            return self.sort, reddit.subreddit(self.sub).top(limit=self.lim)
        elif self.sort == 'hot':
            return self.sort, reddit.subreddit(self.sub).hot(limit=self.lim)
        else:
            self.sort = 'hot'
            print('Sort method was not recognized, defaulting to hot.')
            return self.sort, reddit.subreddit(self.sub).hot(limit=self.lim)
    
    def get_image(self,link):
        image_dir = 'reddit_images/'
        cwd = os.getcwd()
        directory = cwd + "/" + image_dir
        if os.path.isdir(directory):
            pass
        else:
            try:
                os.makedirs(directory,exist_ok=True)
                print("Directory '%s' created successfully" % directory)
            except OSError as error:
                print("Directory '%s' can not be created")
        name = os.path.basename(link)
        if name == "":
            pass
        elif name.isalnum() == False:
            pass
        else:
            print('Name is ',name)
            filename = os.path.join(image_dir, name)
            print('Filename is ',filename)
            if not os.path.isfile(filename):
                urllib.request.urlretrieve(link, filename)

        
    def get_posts(self):

        sub_dict = {'selftext': [], 'title': [], 'id': [], 'sorted_by': [], 'num_comments': [], 'score': [], 'created':[], 'url':[]}
        csv = f'{self.sub}_posts.csv'
        sort, subreddit = self.set_sort()
        df, csv_loaded = (pd.read_csv(csv), 1) if isfile(csv) else ('',0)

        print(f'csv = {csv}')
        print(f'After set_sort(), sort = {sort} and sub = {self.sub}')
        print(f'csv_loaded = {csv_loaded}')

        print(f'Collecting information from r/{self.sub}.')

        for post in subreddit:
            unique_id = post.id not in tuple(df.id) if csv_loaded else True

            if unique_id:
                sub_dict['selftext'].append(post.selftext)
                sub_dict['title'].append(post.title)
                sub_dict['id'].append(post.id)
                sub_dict['sorted_by'].append(sort)
                sub_dict['num_comments'].append(post.num_comments)
                sub_dict['score'].append(post.score)
                sub_dict['created'].append(dt.datetime.fromtimestamp(post.created))
                sub_dict['url'].append(post.url)
                self.get_image(post.url)
            sleep(0.1)
        
        new_df = pd.DataFrame(sub_dict)

        if 'Dataframe' in str(type(df)) and self.mode == 'w+':
            pd.concat([df, new_df], axis=0, sort=0).tto_csv(csv, index=False)
            print(
                f'{len(new_df)} new posts were collected and saved to {csv}')
        elif self.mode == 'w+':
            new_df.to_csv(csv, index=False)
            print(f'{len(new_df)} posts collected and saved to {csv}')
        else:
            print(f'{len(new_df)} posts were collected but they were not added to {csv} because mode was set to "{self.mode}')

class UserInterface(Frame):

    def __init__(self, master):
        Frame.__init__(self,master)
        self.master = master
        master.title('Reddit Scraper')
        self.inputs()

        self.scrape_button = Button(self, text='Initiate Scrape', command=self.scrape)
        self.scrape_button.grid(row=2, column=1, columnspan=2, sticky='w')
        self.grid()

    def inputs(self):
        self.sub_entry = Entry(self, width = 6, font=('Arial',12))
        self.sub_entry.grid(row=0, column=0, columnspan=2, sticky='w')
        self.sub_entry.focus_set()

        sort_dict = {'top', 'new', 'hot'}
        tkvar = StringVar(root)
        tkvar.set('top')
        self.sort_menu = OptionMenu(self, tkvar, *sort_dict)
        self.sort_menu.grid(row=4, column=0, columnspan=2, sticky='w')



    def scrape(self):
        SubredditScraper('pics',lim=100,mode='w+',sort='top').get_posts()

if __name__ == '__main__':
    root = Tk()
    root.geometry()
    ui = UserInterface(root)
    root.mainloop()