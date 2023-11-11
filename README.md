# T-Board
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li><a href="#Project-Description">Project Description</a></li>
    <li><a href="#Future-iterations">Future iterations</a></li>
    <li><a href="#Tools-and-Standards">Tools and Standards</a></li>
        <ul>
            <li><a href="#Built-with">Built with</a></li>
            <li><a href="#Project-Management">Project Management</a></li>
            <li><a href="#Coding-Style">Coding Style</a></li>
        </ul>
    <li><a href="#Getting-Started">Getting Started</a></li>
        <ul>
            <li><a href="#Prerequisites">Prerequisites</a></li>
            <li><a href="#Local-Deployment">Local Deployment</a></li>
        </ul>
    <li><a href="#Contact-Information">Contact Information</a></li>    
  </ol>
</details>

## Project Description
Tboard, tailored for the University of Toronto community, is a user-friendly event dashboard application that facilitates the discovery and management of campus events. Upon registration, users can effortlessly search for events using filters and sort options, such as event type or alphabetical order. The bookmark feature enables users to save and track events they're interested in, with options to view details, delete bookmarks, or download event files. Tboard also offers a rating system, allowing users to provide feedback on attended events, which contributes to an event's overall rating. Users can create and delete their own events, providing a platform for event organization and management. Additionally, the app includes a personal profile management section, where users can view their event history, manage friends, adjust notification settings, and edit their profile, enhancing the overall user experience.

You can access the application at: [T-Board](https://ece444-tboard.onrender.com/)

![Main](/Images_for_documentation/Maindashboard.png)  

## Future iterations
In future releases, we aim to have the following integrated in the application:
* More event types, filters, and sorting options (the three are coupled together)
* Autocomplete search in the search bar
* Friend requests/messaging
* Integrating AI
  * Event recommendation based on user interest
  * Event recommendation based on events that friends have attended and have highly rated 

## Tools and Standards
### Built with 
* [Flask](https://palletsprojects.com/p/flask/)
* [Docker](https://www.docker.com)
* [Figma](https://www.figma.com/)
* [Render](https://www.render.com) 

**Disclaimer: While a majority of the code in this project is written by our team, we openly used ChatGPT to aid our development process.**

### Project Management 
For managing and tracking our progress, we are using [Trello](https://trello.com/).  
You can find our public user story board [here](https://trello.com/b/WXC6CorM/user-story-board).

### Coding Style
Our team is following [Google's Code Style Guide](https://google.github.io/styleguide/).

### Getting Started
#### Prerequisites
These are the prerequisites for our internal team. We will update this section once our project is deployed with instructions for outside contributors.

* Install [Docker](https://www.docker.com)  
* Install virtual environment

#### Local Deployment  
These are the instructions for local deployment:    

1. Activate your virtual environment
2. Download all requirements using 'pip install -r requirements.txt'
3. Set the environment variable to the app.py file (e.g. set FLASK_APP = project/app.py for windows)
4. Delete any existing .db files
5. Run "python -m flask run"
6. Paste local host address into browser of your choice

## Contact Information
* Hui Lee: huijeong.lee@mail.utoronto.ca    
* Daria Moskvitina: daria.moskvitina@mail.utoronto.ca   
* Ghamr Saeed: ghamr.saeed@mail.utoronto.ca 
* An Xi: an.xi@mail.utoronto.ca 
* Jennifer Zhang: jennifer.zhang@mail.utoronto.ca   
* Weihang Zheng: weihang.zheng@mail.utoronto.ca 
