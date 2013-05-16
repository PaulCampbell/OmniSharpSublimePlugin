
import sublime
import sublime_plugin
import os
import urllib2, urllib, urlparse, json

class OmniSharp(sublime_plugin.EventListener):
    settings = None
    word_list = []

    def on_modified(self, view):
        self.view = view
        sublime.set_timeout(lambda: self.load_completions(view), 3)

    def load_completions(self, view):
        scope_name = view.scope_name(view.sel()[0].begin())  
        if self.should_trigger(scope_name) : 
            completions = self.get_response() 
            print completions
            for completion in completions:
                self.word_list.append(completion['CompletionText'])

    def should_trigger(self, scope):
        if ".cs" in scope : 
            return True
        return False
       

    def get_autocomplete_list(self, word):
        autocomplete_list = []
        for w in self.word_list:
            try:
                if word.lower() in w.lower():
                    autocomplete_list.append((w, w))
            except UnicodeDecodeError:
                continue

        return autocomplete_list



    # gets called when auto-completion pops up.
    def on_query_completions(self, view, prefix, locations):
        scope_name = sublime.windows()[0].active_view().scope_name(sublime.windows()[0].active_view().sel()[0].begin())
        return self.get_autocomplete_list(prefix)

    def get_response(self):
        parameters = {}
        location = self.view.sel()[0]
        cursor = self.view.rowcol(location.begin()) 
        parameters['line'] = cursor[0] + 1
        parameters['column'] = cursor[1] + 1
        parameters['wordToComplete'] =  self.view.substr(self.view.word(location.a))
        parameters['buffer'] = '\r\n'.join(self.task_input()[:])
        parameters['filename'] = self.view.file_name()

        target = 'http://localhost:2000/autocomplete'
        parameters = urllib.urlencode(parameters)
        response = urllib2.urlopen(target, parameters)

        js = response.read()

        if(js != ''):
            return json.loads(js) 

    def task_input(self):
        selections = [region for region in self.view.sel() if not region.empty()]
        if len(selections) == 0:
            self.regions = [sublime.Region(0, self.view.size())]
        else:
            self.regions = selections

        page_text = [self.view.substr(region).encode('utf-8') for region in self.regions]
        return page_text