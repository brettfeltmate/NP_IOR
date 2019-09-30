# -*- coding: utf-8 -*-

__author__ = "Brett Feltmate"

import klibs
from klibs import P
from klibs.KLUtilities import deg_to_px, point_pos, midpoint, smart_sleep, hide_mouse_cursor, line_segment_len
from klibs.KLUserInterface import ui_request, key_pressed, any_key
from klibs.KLCommunication import message
from klibs.KLResponseCollectors import ResponseCollector, RC_KEYPRESS, KeyMap, ResponseListener, Response
from klibs.KLGraphics import fill, blit, flip
from klibs.KLGraphics import KLDraw as kld
from klibs.KLConstants import TK_MS, STROKE_CENTER
from klibs.KLTrialFactory import BlockIterator, TrialFactory
from klibs.KLTime import CountDown

import sdl2

WHITE = [255, 255, 255, 255]
GREEN = [0, 255, 0, 255]


class NP_IOR(klibs.Experiment):

    def setup(self):

        box_size   = deg_to_px(1.8)
        box_thick  = deg_to_px(0.05)
        stim_size  = deg_to_px(0.95)
        stim_thick = deg_to_px(0.1)
        fix_size   = deg_to_px(1)
        fix_offset = deg_to_px(2.8)

        box_stroke = [box_thick, WHITE, STROKE_CENTER]

        self.txtm.add_style(label='greentext', color=GREEN)

        self.target     = kld.Annulus(diameter=stim_size,   thickness=stim_thick, fill=WHITE)
        self.distractor = kld.FixationCross(size=stim_size, thickness=stim_thick, fill=WHITE)

        # Set the rotation of placeholder boxes & fixation to match that of the display (diamond, square)
        rotate = 45 if P.condition == 'diamond' else 0
        self.placeholder = kld.Rectangle(width=box_size, stroke=box_stroke, rotation=rotate)
        self.fixation    = kld.Asterisk(size=fix_size, thickness=stim_thick, fill=WHITE, rotation=rotate, spokes=8)

        # Which locations are labelled far or near is dependent on arrangement of display
        # 'near' locations refer to those that lie at the intersection of 'far' locations
        if P.condition == 'square':
            self.far_locs = {
                1: [point_pos(P.screen_c, amplitude=fix_offset, angle=315, clockwise=True), 'NorthEast'],
                2: [point_pos(P.screen_c, amplitude=fix_offset, angle=45,  clockwise=True), 'SouthEast'],
                3: [point_pos(P.screen_c, amplitude=fix_offset, angle=135, clockwise=True), 'SouthWest'],
                4: [point_pos(P.screen_c, amplitude=fix_offset, angle=225, clockwise=True), 'NorthWest']
            }

            self.near_locs = {
                5: [midpoint(self.far_locs[4][0], self.far_locs[1][0]), 'North'],
                6: [midpoint(self.far_locs[1][0], self.far_locs[2][0]), 'East'],
                7: [midpoint(self.far_locs[3][0], self.far_locs[2][0]), 'South'],
                8: [midpoint(self.far_locs[3][0], self.far_locs[4][0]), 'West']
            }

        else:  # if P.condition == 'diamond'
            self.far_locs = {
                1: [point_pos(P.screen_c, amplitude=fix_offset, angle=270, clockwise=True), 'North'],
                2: [point_pos(P.screen_c, amplitude=fix_offset, angle=0,   clockwise=True), 'East'],
                3: [point_pos(P.screen_c, amplitude=fix_offset, angle=90,  clockwise=True), 'South'],
                4: [point_pos(P.screen_c, amplitude=fix_offset, angle=180, clockwise=True), 'West']
            }

            self.near_locs = {
                5: [midpoint(self.far_locs[4][0], self.far_locs[1][0]), 'NorthWest'],
                6: [midpoint(self.far_locs[1][0], self.far_locs[2][0]), 'NorthEast'],
                7: [midpoint(self.far_locs[3][0], self.far_locs[2][0]), 'SouthEast'],
                8: [midpoint(self.far_locs[3][0], self.far_locs[4][0]), 'SouthWest']
            }

        if not P.development_mode:
            self.keymap = KeyMap(
                'directional_response',
                ['North', 'NorthEast', 'East', 'SouthEast',
                 'South', 'SouthWest', 'West', 'NorthWest'],
                ['North', 'NorthEast', 'East', 'SouthEast',
                 'South', 'SouthWest', 'West', 'NorthWest'],
                [sdl2.SDLK_KP_8, sdl2.SDLK_KP_9, sdl2.SDLK_KP_6, sdl2.SDLK_KP_3,
                 sdl2.SDLK_KP_2, sdl2.SDLK_KP_1, sdl2.SDLK_KP_4, sdl2.SDLK_KP_7]
            )

        else:  # Don't have a numpad myself, so I need an alternative when developing
            self.keymap = KeyMap(
                'directional_response',
                ['North', 'NorthEast', 'East', 'SouthEast',
                 'South', 'SouthWest', 'West', 'NorthWest'],
                ['North', 'NorthEast', 'East', 'SouthEast',
                 'South', 'SouthWest', 'West', 'NorthWest'],
                [sdl2.SDLK_i, sdl2.SDLK_o, sdl2.SDLK_l, sdl2.SDLK_PERIOD,
                 sdl2.SDLK_COMMA, sdl2.SDLK_m, sdl2.SDLK_j, sdl2.SDLK_u]
            )

        # Prime items always presented in far locations
        self.prime_locs = self.far_locs.copy()
        # Probe items can be far or near, determined conditionally
        self.probe_locs = dict(self.near_locs.items() + self.far_locs.items())

        # So, to get a practice block of 25, we first need to generate the full set of 2048
        # possible permutations, trim that down to the 288 legitimate permutations,
        # then trim that down to 25...
        self.insert_practice_block(1, 2048)

        # Because KLibs auto-generates trials for each product of ind_vars.py,
        # a lot of 'vestigial' trials are generated that we don't want, this sorts
        # through the trial list and removes those trials.
        for ind_b, block in enumerate(self.trial_factory.blocks):
            for trial in block:

                # targets & distractors cannot overlap within a given display
                if trial[1] == trial[2] or trial[3] == trial[4]:

                    self.trial_factory.blocks[ind_b].remove(trial)
                    block.i -= 1
                    block.length = len(block.trials)
                    continue
                # For 'near' trials, Ts & Ds cannot appear at 'far' locations
                if trial[0] == 'near':
                    if trial[3] < 5 or trial[4] < 5:

                        self.trial_factory.blocks[ind_b].remove(trial)
                        block.i -= 1
                        block.length = len(block.trials)

                # Conversely, cannot appear at 'near' locations on 'far' trials
                else:
                    if trial[3] > 4 or trial[4] > 4:

                        self.trial_factory.blocks[ind_b].remove(trial)
                        block.i -= 1
                        block.length = len(block.trials)

            # We only want 25 trials for practice, this trims the block
            # to the appropriate length
            if ind_b == 0:
                for trial in block:
                    self.trial_factory.blocks[ind_b].remove(trial)
                    block.i -= 1
                    block.length = len(block.trials)

                    if block.length == 25:
                        break

        # Set to True once instructions are provided
        self.instructed = False

    def block(self):
        # Only present instructions the first time.
        if not self.instructed:
            self.instructed = True
            self.give_instructions()

        # Inform as to block progress
        if P.practicing:
            msg = message("PRACTICE ROUND\n\nPress '5' to begin...", blit_txt=False)

        else:
            msg = message("TESTING ROUND\n\nPress '5' to begin...", blit_txt=False)

        fill()
        blit(msg, location=P.screen_c, registration=5)
        flip()

        # Hangs until '5' key
        self.continue_on()


    def setup_response_collector(self):
        self.probe_rc = ResponseCollector(uses=RC_KEYPRESS)
        self.prime_rc = ResponseCollector(uses=RC_KEYPRESS)

        self.prime_rc.display_callback = self.present_filled_array
        self.prime_rc.display_kwargs = {'display': 'prime'}
        self.prime_rc.terminate_after = [5000, TK_MS]
        self.prime_rc.keypress_listener.interrupts = True
        self.prime_rc.keypress_listener.key_map = self.keymap

        self.probe_rc.display_callback = self.present_filled_array
        self.probe_rc.display_kwargs = {'display': 'probe'}
        self.probe_rc.terminate_after = [5000, TK_MS]
        self.probe_rc.keypress_listener.interrupts = True
        self.probe_rc.keypress_listener.key_map = self.keymap

    def trial_prep(self):
        # Grab locations (and their cardinal labels) for each T & D
        self.T_prime_loc = list(self.prime_locs[self.prime_target])
        self.D_prime_loc = list(self.prime_locs[self.prime_distractor])
        self.T_probe_loc = list(self.probe_locs[self.probe_target])
        self.D_probe_loc = list(self.probe_locs[self.probe_distractor])

        # Grab distance between each item pair
        self.T_prime_to_T_probe = line_segment_len(self.T_prime_loc[0], self.T_probe_loc[0])
        self.T_prime_to_D_probe = line_segment_len(self.T_prime_loc[0], self.D_probe_loc[0])
        self.D_prime_to_T_probe = line_segment_len(self.D_prime_loc[0], self.T_probe_loc[0])
        self.D_prime_to_D_probe = line_segment_len(self.D_prime_loc[0], self.D_probe_loc[0])

        # Once locations selected, determine which trial type this trial would fall under.
        self.trial_type = self.determine_trial_type()

        # Hide mouse cursor throughout trial
        hide_mouse_cursor()

        # Present fixation & start trial
        self.present_fixation()

    def trial(self):
        hide_mouse_cursor()

        # Begin with empty array...
        self.present_empty_array()

        smart_sleep(500)

        # 500ms later present prime array & record response
        self.prime_rc.collect()

        # If response, log, otherwise NA
        response_prime, rt_prime = 'NA', 'NA'

        if len(self.prime_rc.keypress_listener.response()):
            response_prime, rt_prime = self.prime_rc.keypress_listener.response()

        # Reset to empty array following response
        self.present_empty_array()

        smart_sleep(300)

        # 300ms later present probe array
        self.probe_rc.collect()

        response_probe, rt_probe = 'NA', 'NA'

        if len(self.probe_rc.keypress_listener.response()):
            response_probe, rt_probe = self.probe_rc.keypress_listener.response()

        # Determine accuracy of responses (i.e., whether target selected)
        prime_correct = response_prime == self.T_prime_loc[1]
        probe_correct = response_probe == self.T_probe_loc[1]

        # Present feedback on performance (mean RT for correct, 'WRONG' for incorrect)
        self.present_feedback(prime_correct, rt_prime, probe_correct, rt_probe)

        prime_choice, probe_choice = 'NA', 'NA'

        if response_prime == self.T_prime_loc[1]:
            prime_choice = 'target'
        elif response_prime == self.D_prime_loc[1]:
            prime_choice = 'distractor'
        else:
            prime_choice = "empty_cell"

        if response_probe == self.T_probe_loc[1]:
            probe_choice = 'target'
        elif response_probe == self.D_probe_loc[1]:
            probe_choice = 'distractor'
        else:
            probe_choice = "empty_cell"

        return {
            "block_num":            P.block_number,
            "trial_num":            P.trial_number,
            "practicing":           str(P.practicing),
            "far_near":             self.far_or_near,
            'trial_type':           self.trial_type,
            'prime_rt':             rt_prime,
            'probe_rt':             rt_probe,
            'prime_correct':        str(prime_correct),
            'probe_correct':        str(probe_correct),
            't_prime_to_t_probe':   self.T_prime_to_T_probe,
            't_prime_to_d_probe':   self.T_prime_to_D_probe,
            'd_prime_to_t_probe':   self.D_prime_to_T_probe,
            'd_prime_to_d_probe':   self.D_prime_to_D_probe,
            'prime_choice':         prime_choice,
            'probe_choice':         probe_choice,
            'prime_response':       response_prime,
            'probe_response':       response_probe,
            't_prime_loc':          self.T_prime_loc[1],
            'd_prime_loc':          self.D_prime_loc[1],
            't_probe_loc':          self.T_probe_loc[1],
            'd_probe_loc':          self.D_probe_loc[1]
        }

    def trial_clean_up(self):

        # Provide break 1/2 through experimental block
        if P.trial_number == P.trials_per_block / 2:
            txt = "You're 1/2 through, take a break if you like\nand press '5' when you're ready to continue"
            msg = message(txt, blit_txt=False)

            fill()
            blit(msg, location=P.screen_c, registration=5)
            flip()

            while True:
                if key_pressed(key=sdl2.SDLK_KP_5):
                    break

    # When called, hangs until appropriate key is depressed
    def continue_on(self):
        while True:
            if not P.development_mode:
                if key_pressed(key=sdl2.SDLK_KP_5):
                    break

            else:
                if key_pressed(key=sdl2.SDLK_k):
                    break

    def present_fixation(self):
        fill()
        blit(self.fixation, location=P.screen_c, registration=5)
        flip()

        self.continue_on()

    def present_feedback(self, prime_correct, prime_rt, probe_correct, probe_rt):

        prime_fb = prime_rt if prime_correct else 'WRONG'
        probe_fb = probe_rt if probe_correct else 'WRONG'

        fb_txt = "{0}\n{1}".format(prime_fb, probe_fb)

        fb = message(fb_txt, align='center', blit_txt=False)

        countdown = CountDown(1)
        while countdown.counting():
            fill()
            blit(fb, location=P.screen_c, registration=5)
            flip()



    def present_empty_array(self):
        fill()
        for value in self.probe_locs.values():
            blit(self.placeholder, registration=5, location=value[0])
        blit(self.fixation, location=P.screen_c, registration=5)
        flip()

    def present_filled_array(self, display):
        fill()
        for value in self.probe_locs.values():
            blit(self.placeholder, registration=5, location=value[0])

        if display == 'prime':
            blit(self.target, registration=5, location=self.T_prime_loc[0])
            blit(self.distractor, registration=5, location=self.D_prime_loc[0])
        else:
            blit(self.target, registration=5, location=self.T_probe_loc[0])
            blit(self.distractor, registration=5, location=self.D_probe_loc[0])

        blit(self.fixation, location=P.screen_c, registration=5)
        flip()


    def determine_trial_type(self):

        if self.far_or_near == 'far':

            if (self.T_prime_loc, self.D_prime_loc) == (self.T_probe_loc, self.D_probe_loc):
                return 'repeat'

            elif (self.T_prime_loc, self.D_prime_loc) == (self.D_probe_loc, self.T_probe_loc):
                return 'switch'

            elif (self.T_prime_loc != self.T_probe_loc) and (self.D_prime_loc != self.D_probe_loc) and \
                 (self.T_prime_loc != self.D_probe_loc) and (self.D_prime_loc != self.T_probe_loc):
                return 'control-far'

            elif (self.T_prime_loc == self.T_probe_loc) and (self.D_prime_loc != self.D_probe_loc):
                return 'T.to.T-far'

            elif (self.D_prime_loc == self.D_probe_loc) and (self.T_prime_loc != self.T_probe_loc):
                return 'D.to.D-far'

            elif (self.D_probe_loc == self.T_prime_loc) and (self.T_probe_loc != self.D_prime_loc):
                return 'D.to.T-far'

            elif (self.T_probe_loc == self.D_prime_loc) and (self.D_probe_loc != self.T_prime_loc):
                return 'T.to.D-far'

            else:
                print "[FAR] - unanticipated display arrangement / trial type for trial {0}".format(P.trial_number)
                return 'erroneous'

        else:

            if self.T_probe_loc[0] == midpoint(self.T_prime_loc[0], self.D_prime_loc[0]):
                return 'T.at.CoG-near'

            elif self.D_probe_loc[0] == midpoint(self.T_prime_loc[0], self.D_prime_loc[0]):
                return 'D.at.CoG-near'

            else:
                return 'control-near'

    def give_instructions(self):
        button_map = {
            'North':     message("8", align='center', blit_txt=False, style='greentext'),
            'East':      message("6", align='center', blit_txt=False, style='greentext'),
            'South':     message("2", align='center', blit_txt=False, style='greentext'),
            'West':      message("4", align='center', blit_txt=False, style='greentext'),
            'NorthEast': message("9", align='center', blit_txt=False, style='greentext'),
            'NorthWest': message("7", align='center', blit_txt=False, style='greentext'),
            'SouthWest': message("1", align='center', blit_txt=False, style='greentext'),
            'SouthEast': message("3", align='center', blit_txt=False, style='greentext')
        }


        hide_mouse_cursor()

        txt = ("In this experiment, your task is to indicate the location of the target 'o'\n"
               "while ignoring the distractor '+'."
               "\n\n(press the '5' on the numpad to continue past each message)")

        instruction_msg = message(txt, align='center', blit_txt=False)


        fill()
        blit(instruction_msg, location=P.screen_c, registration=5)
        flip()

        self.continue_on()

        txt = ("Each trial will begin with a fixation cross, when you see this\n"
               "you may begin the trial by pressing the '5' key on the numpad.\n"
               "Shortly after which an array will appear")

        instruction_msg = message(txt, align='center', blit_txt=False)

        fill()
        blit(instruction_msg, location=(P.screen_c[0], int(P.screen_c[1] * 0.3)), registration=5)
        blit(self.fixation, location=P.screen_c, registration=5)
        flip()

        self.continue_on()

        fill()
        blit(instruction_msg, location=(P.screen_c[0], int(P.screen_c[1] * 0.3)), registration=5)
        for value in self.probe_locs.values():
            blit(self.placeholder, registration=5, location=value[0])
        blit(self.fixation, location=P.screen_c, registration=5)
        flip()

        self.continue_on()

        txt = ("Shortly after the array appears, both the target 'o' and distractor '+'\n"
               "will appear in random locations within the array...")

        instruction_msg = message(txt, align='center', blit_txt=False)

        t_loc = self.prime_locs[1][0]
        d_loc = self.prime_locs[3][0]

        fill()
        blit(instruction_msg, location=(P.screen_c[0], int(P.screen_c[1] * 0.3)), registration=5)
        for value in self.probe_locs.values():
            blit(self.placeholder, registration=5, location=value[0])
        blit(self.target, location=t_loc, registration=5)
        blit(self.distractor, location=d_loc, registration=5)
        blit(self.fixation, location=P.screen_c, registration=5)
        flip()

        self.continue_on()

        txt = ("Once they appear, please indicate the location of the 'o' as quickly and\n"
               "accurately as possible, using the numpad ('8' for North, '9' for Northeast, etc.,)\n"
               "Each trial will actually consist of two displays, each requiring their own response,\n"
               "one after the other")

        instruction_msg = message(txt, align='center', blit_txt=False)

        fill()
        blit(instruction_msg, location=(P.screen_c[0], int(P.screen_c[1] * 0.3)), registration=5)
        for value in self.probe_locs.values():
            blit(self.placeholder, registration=5, location=value[0])
            blit(button_map[value[1]], registration=5, location=value[0])
        blit(self.target, location=t_loc, registration=5)
        blit(self.distractor, location=d_loc, registration=5)
        blit(self.fixation, location=P.screen_c, registration=5)
        flip()

        self.continue_on()

        txt = ("Once you have made both responses, you will be provided with feedback,\n"
               "the upper and lower line referring to your performance\n"
               "in the first and second display, respectively.\n")

        instruction_msg = message(txt, align='center', blit_txt=False)

        fill()
        blit(instruction_msg, location=P.screen_c, registration=5)
        flip()

        self.continue_on()

        txt = "For correct responses, your reaction time will be provided to you."
        fb_txt = "360\n412"

        instruction_msg = message(txt, align='center', blit_txt=False)
        fb_msg = message(fb_txt, align='center', blit_txt=False)

        fill()
        blit(instruction_msg, location=(P.screen_c[0], int(P.screen_c[1] * 0.3)), registration=5)
        blit(fb_msg, location=P.screen_c, registration=5)
        flip()

        self.continue_on()

        txt = "For incorrect responses, your reaction time will be replaced by the word WRONG."
        fb_txt = "323\nWRONG"

        instruction_msg = message(txt, align='center', blit_txt=False)
        fb_msg = message(fb_txt, align='center', blit_txt=False)

        fill()
        blit(instruction_msg, location=(P.screen_c[0], int(P.screen_c[1] * 0.3)), registration=5)
        blit(fb_msg, location=P.screen_c, registration=5)
        flip()

        self.continue_on()

        continue_txt = ("Throughout the task, please keep your fingers rested on the numpad,\n"
                        "with your middle finger resting on the '5' key\n\n"
                        "The experiment will begin with a short practice round to familiarize you with the task\n\n"
                        "When you're ready, press the '5' key to begin...")

        continue_msg = message(continue_txt, align='center', blit_txt=False)


        fill()
        blit(continue_msg, location=P.screen_c, registration=5)
        flip()

        self.continue_on()

    def clean_up(self):
        pass
