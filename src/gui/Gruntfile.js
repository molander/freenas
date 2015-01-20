// Generated by generator-rotor 0.1.0
// 2014-09-20
"use strict";

var _    = require("lodash");
var glob = require("glob");


// Gruntfile
// =============================================================================
// This file is the 'control panel' for the entire project. Grunt is a
// JavaScript task runner, capable of automating, parallelizing, and simplifying
// common development tasks.

// Wrapper function for Grunt
module.exports = function(grunt) {

  // Force use of Unix newlines
  grunt.util.linefeed = "\n";

  // Show a breakdown of build times, useful for debugging
  // require("time-grunt")(grunt);

  // GRUNT CONFIGURATION AND GLOBAL VARIABLES
  // Load task configurations from grunt_tasks/config
  function loadConfig( path ) {
    var object = {};
    var ConfigFile;
    var key;

    // Iterate over all config module files, and create a single config object.
    glob.sync( "*", { cwd: path } ).forEach( function( option ) {
      // Each task file contains a constructor capable of creating a
      // representative options object for its task.
      ConfigFile = require(path + option);
      key = option.replace( /\.js$/, "" );
      // Invoke constructor, append output to configuration object, keyed by the
      // name of its task.
      object[key] = new ConfigFile( grunt );
    });

    return object;
  }


  // Configuration environment and global variables
  var gruntConfig = {
    // Use npm manifest as a list of available packages
    pkg: grunt.file.readJSON("package.json")

    // DEVELOPMENT VARIABLES
    // =========================================================================
    // These are some variables that commonly change during development, and
    // will simplify any changes to file structure, ports, etc.

    , dirTree: {
          client : "app/client"
        , server : "app/server"
        , routes : "app/routes"
        , data   : "app/data"

        // Bower components
        , bower: {
            velocity     : "./bower_components/velocity"
          , openSans: {
              less  : "./bower_components/lessfonts-open-sans/src/less"
            , fonts : "./bower_components/lessfonts-open-sans/dist/fonts/OpenSans"
          }
          , fontawesome: {
              less  : "./bower_components/fontawesome/less"
            , fonts : "./bower_components/fontawesome/fonts"
          },
        }

        // Sources
        , source: {
            root      : "app"
          , images    : "app/source/images"
          , favicons  : "app/source/favicons"
          , jsx       : "app/jsx"
          , styles    : "app/source/styles"
          , templates : "app/templates"
        }

        // Build
        , build: {
            root : "app/build/"
          , app  : "app/build/js"
          , img  : "app/build/img"
          , css  : "app/build/css"
          , font : "app/build/font"
          , dist : "app/build/js"
        }

        , deployment : "app-deploy"
    }

    // Environment
    , env: {
        port   : 4000
    }

    // FreeNAS remote config
    , configFilePath : {
        "freenasNine" : "./freenas9-conf.json"
      , "freenasTen"  : "./freenas10-conf.json"
    }
    , freenasVersion : null
    , freenasConfig  : {
        "notConfigured" : true
      , "remoteHost"    : null
      , "sshPort"       : null
      , "authType"      : null
      , "keyPath"       : null
      , "rootPass"      : null
      , "freeNASPath"   : null
    }
  };

  // Load external configuration files
  _.assign( gruntConfig, loadConfig( "./grunt_tasks/config/" ) );

  grunt.initConfig( gruntConfig );


  // LOAD GRUNT TASKS FROM NPM
  // ===========================================================================
  // Here, we tell grunt to load the packages from package.json. Tasks must be
  // loaded before they can be called.

  require("load-grunt-tasks")( grunt );


  // LOAD OTHER GRUNT TASKS
  // ===========================================================================
  // This section contains grunt tasks which have been defined locally, not via
  // npm. Configuration tools and modularized grunt tasks belong here.

  // Registers task: 'bootstrap', installed as local module
  grunt.loadTasks("grunt_tasks");


  // DEFAULT
  // When "grunt" is run with no arguments, run "develop". This will run
  // environment and dependency checkers, manage the FreeNAS remote config file,
  // and bootstrap the FreeNAS environment.

  // Options
  // --local   Start a local dev server, ignore any config files.
  grunt.registerTask( "default", [ "develop" ] );
};