from os.path import isfile
import os
import praw
import prawcore
import pandas as pd
from time import sleep
import datetime as dt
import urllib.request
from tkinter import *
from PIL import Image, ImageTk

#Importing credentials to use Reddit's API
reddit = praw.Reddit("credentials")

"""
This is the Reddit Scraper that scrapes submission text and images

"""
class SubredditScraper:
    
    def __init__(self, sub, sort, lim, mode):
        self.sub = sub
        self.sort = sort
        self.lim = lim
        self.mode = mode

        print(f'SubredditScraper instance created with values sub = {sub}, sort = {sort}, lim = {lim}, mode= {mode}')
    
    #This is the method for changing the scraper based on the defined sort method
    def set_sort(self):
        if self.sort == 'new':
            return self.sort, reddit.subreddit(self.sub).new(limit=self.lim)
        elif self.sort == 'top':
            return self.sort, reddit.subreddit(self.sub).top(limit=self.lim)
        elif self.sort == 'hot':
            return self.sort, reddit.subreddit(self.sub).hot(limit=self.lim)
        else:
            self.sort = 'hot'
            ui.updates('Sort method was not recognized, defaulting to hot.')
            return self.sort, reddit.subreddit(self.sub).hot(limit=self.lim)
    
    #This is the image downloader
    def get_image(self,link):
        image_dir = 'reddit_images/'
        cwd = os.getcwd()
        directory = cwd + "/" + image_dir
        #Checking for existing directory and created if non existant
        if os.path.isdir(directory):
            pass
        else:
            try:
                os.makedirs(directory,exist_ok=True)
                print("Directory '%s' created successfully" % directory)
            except OSError as error:
                print("Directory '%s' can not be created")
        name = os.path.basename(link)
        #This renames the file and downloads if able
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

    #This is the actual scraper
    def get_posts(self):

        #Setting dictonary for what information we want to scrape and checking csv
        sub_dict = {'selftext': [], 'title': [], 'id': [], 'sorted_by': [], 'num_comments': [], 'score': [], 'created':[], 'url':[]}
        csv = f'{self.sub}_posts.csv'
        sort, subreddit = self.set_sort()
        df, csv_loaded = (pd.read_csv(csv), 1) if isfile(csv) else ('',0)

        print(f'csv = {csv}')
        print(f'After set_sort(), sort = {sort} and sub = {self.sub}')
        print(f'csv_loaded = {csv_loaded}')

        ui.updates(f'Collecting information from r/{self.sub}.')

        #Scraping posts and calling image scraper if the post has not already been scraped
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
            sleep(0.1)
            self.get_image(post.url)

        #Putting into pandas to export post data to csv
        new_df = pd.DataFrame(sub_dict)
        if 'Dataframe' in str(type(df)) and self.mode == 'w+':
            pd.concat([df, new_df], axis=0, sort=0).tto_csv(csv, index=False)
            ui.updates(f'{len(new_df)} new posts were collected and saved to {csv}')
        elif self.mode == 'w+':
            new_df.to_csv(csv, index=False)
            ui.updates(f'{len(new_df)} posts collected and saved to {csv}')
        else:
            print(f'{len(new_df)} posts were collected but they were not added to {csv} because mode was set to "{self.mode}')

"""
This is the GUI for the Scraper

"""
class UserInterface(Frame):

    def __init__(self, master):
        #loading everything
        Frame.__init__(self,master)
        self.master = master
        master.title('Reddit Scraper')
        master.configure(background='#121212')
        master.attributes('-alpha',0.9)
        self.configure(background='#121212')
        self.inputs()

        #Scraper button
        img = PhotoImage(file = r"C:\Users\Vex\Documents\GitHub\RedditScraper\resources\scraperbutton.png")
        img = img.subsample(1,1)
        #img = img.subsample(5,5)
        self.scrape_button = Button(self, text='Initiate Scrape', font=('Montserrat',9), fg='#BB86FC', command=self.scrape, image = img, compound = CENTER, borderwidth=0, highlightthickness=0, padx=0, pady=0)
        self.scrape_button.grid(row=3, column=1, sticky='S')
        self.scrape_button.image = img

        #setting up grid
        self.grid()
        col_count, row_count = self.grid_size()
        for col in range(col_count):
            self.grid_columnconfigure(col, minsize=80, weight=1)
        for row in range(row_count):
            self.grid_rowconfigure(row, minsize=60, weight=1)

    #This sets up all the widgets for user input
    def inputs(self):
        #Subreddit entry
        self.sub_entry = Entry(self, width=12, font=('Montserrat',10))
        self.sub_entry.grid(row=0, column=1)
        self.sub_lbl = Label(self, text='Enter the desired Subreddit:', font=('Montserrat',10,'bold'), bg='#121212', fg='white')
        self.sub_lbl.grid(row=0)

        #Sort method
        sort_dict = {'top', 'new', 'hot'}
        self.tkvar = StringVar(root)
        self.tkvar.set('top')
        self.sort_menu = OptionMenu(self, self.tkvar, *sort_dict)
        self.sort_menu.grid(row=1, column=1)
        self.sort_lbl = Label(self, text='Select the sorting method: ', font=('Montserrat',10,'bold'), bg='#121212', fg='white')
        self.sort_lbl.grid(row=1)

        #Post number limit
        self.lim_entry = Entry(self, width=8, font=('Arial',10))
        self.lim_entry.grid(row=2, column=1)
        self.lim_lbl = Label(self, text='Enter the amount of posts to download (Max 1000): ', font=('Montserrat',10,'bold'), bg='#121212', fg='white')
        self.lim_lbl.grid(row=2)

    #This calls the scraper and checks for existing subreddit and that entries are filled out
    def scrape(self):
        sub_in = self.sub_entry.get()
        sort_in = self.tkvar.get()
        try:
            limit_in = int(self.lim_entry.get())
        except ValueError:
            self.updates('Please enter a limit.')
        if sub_in == '':
            self.updates('Please enter a subreddit.')
        elif limit_in == 0:
            self.updates('Please enter a limit.')
        else:
            if limit_in <= 1000:
                try:
                    #Scraper is called
                    SubredditScraper(sub=sub_in,lim=limit_in,mode='w+',sort=sort_in).get_posts()
                except prawcore.exceptions.Redirect:
                    self.updates(f'Please check that {sub_in} is an existing subreddit.')
            else:
                self.updates('Error post download limit is 1000')

    #This sets up the progress updates and error messaging in the GUI
    def updates(self,message):
        self.update_lbl = Label(self, text=message, font=('Montserrat',10,'bold'), bg='#121212', fg='#CF6679')
        self.update_lbl.grid(row=3, column=0, sticky='S')
        self.update()

#Calling up the UI if this file is being called directly
if __name__ == '__main__':
    root = Tk()
    root.geometry('500x300')
    ui = UserInterface(root)
    root.mainloop()