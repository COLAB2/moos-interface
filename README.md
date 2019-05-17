# Moos-interface
This is the python interface with Moos for the AGDA Project

# INSTALLATION INSTRUCTIONS

1. Download MOOS-IVP
```
   $ svn co https://oceanai.mit.edu/svn/moos-ivp-aro/releases/moos-ivp-17.7.2 moos-ivp
```
2. Navigate to the moos-ivp directory you recently downloaded, you will find seperate README files for the installation instructions depending on the platform you are using. Please follow those instuctions and install moos-ivp.

3. Navigate to the moos-ivp directory, and clone the moos-ivp-midca directory. Change the branch to moos_agda
```
  $ cd moos-ivp
  $ git clone https://github.com/COLAB2/moos-ivp-midca.git
  $ git checkout moos_agda
```
4. Add moos-ivp and moos-ivp-midca directory to the path variable
```
   $ sudo nano ~/.bash_profile
   copy the path of your moos-ivp/bin and moos-ivp-midca/bin directories to your path variable
   
   For example, adapt and copy the below two lines to the editor, save and close
   # for Moos - IVP
   export PATH="/Users/user-name/moos-ivp/bin:$PATH"

   # for Moos-ivp-midca
   export PATH="/Users/user-name/moos-ivp/moos-ivp-midca/bin:$PATH"
```
5. Navigate to the moos-ivp-midca directory, you will find a README file follow the instruction to install moos-ivp-midca
6. Navigate to the moos-ivp/ivp/src directory, delete the folder named "uFldHazardSensor" and follow the instructions below
```
    $ cd moos-ivp/ivp/src
    $ git clone https://github.com/COLAB2/uFldHazardSensor.git
    $ cd ..
    $ cd ..
    $ ./build-ivp.sh
```
7. Install Zmq from the website http://zeromq.org/intro:get-the-software
8. Clone the current repository to a local path in the machine
```
$ git clone https://github.com/COLAB2/moos-interface.git
```

# Run the Demo

Run the mooos applications 
```
$ cd moos-ivp/moos-ivp-midca/missions/gatars
$ ./clean.sh 
$ ./launch.sh 
A GUI Window will appear, please hit Deploy button.
```
Run the python file in a seperate window (navigate to the cloned moos-interface repository)
```
$ cd moos-interface
$ python world.py
```

