# Where is he working?
# About
Консольное приложение для получения информации о работодателях участников группы vk.com и их друзьях с того же факультета<br />
Console application for obtaining information about employers of vk.com group members and their friends from same faculties

## Setting up
```sh
$ git clone https://github.com/26twentysix/whereIsHeWorking.git
$ cd whereIsHeWorking
```
This app is using environment variables, so before start create file .env in app root directory and insert your vk.com api access token (You can check .env.example file to understand how it must be) <br />
Settings are in src/app/util/settings.py , you can change them if you want to get specified result

### Run app
```sh
$ python start.py
```
