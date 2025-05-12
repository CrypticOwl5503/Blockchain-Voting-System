"""
Command-line admin interface for blockchain voting system.
"""
import os
import sys
import cmd
import json
import time
import getpass
from admin.auth import AdminAuth
from admin.election import Election
from admin.candidates import CandidateManager
from admin.reports import ReportGenerator

class AdminInterface(cmd.Cmd):
    intro = "Blockchain Voting System - Admin Interface"
    prompt = "admin> "
    
    def __init__(self, blockchain):
        super().__init__()
        self.blockchain = blockchain
        self.auth = AdminAuth()
        self.election = Election(blockchain)
        self.candidates = CandidateManager(self.election)
        self.reports = ReportGenerator(blockchain, self.election)
        self.current_user = None
        self.token = None
        
    def preloop(self):
       
        # Check if any admin exists
        if not self.auth.admins:
            print("No admin accounts found. Creating default admin account.")
            username = input("Enter admin username: ")
            password = getpass.getpass("Enter admin password: ")
            success, message = self.auth.create_admin(username, password, role="super_admin")
            if success:
                print("Admin account created successfully.")
            else:
                print(f"Error creating admin account: {message}")
    
    def emptyline(self):
       
        pass
        
    def default(self, line):
        """Handle unknown commands."""
        print(f"Unknown command: {line}")
        print("Type 'help' to see available commands.")
    
    def do_login(self, arg):
        
        if self.current_user:
            print(f"Already logged in as {self.current_user}")
            return
            
        username = input("Username: ")
        password = getpass.getpass("Password: ")
        
        success, result = self.auth.authenticate(username, password)
        if not success:
            print(f"Authentication failed: {result}")
            return
            
        print(f"OTP code: {result['otp']}")
        otp = input("Enter OTP code: ")
        
        success, result = self.auth.verify_otp(username, otp)
        if not success:
            print(f"OTP verification failed: {result}")
            return
            
        self.token = result["token"]
        self.current_user = username
        self.prompt = f"admin({username})> "
        print(f"Logged in as {username}")
    
    def do_logout(self, arg):
        
        if not self.current_user:
            print("Not logged in")
            return
            
        self.auth.logout(self.token)
        self.token = None
        self.current_user = None
        self.prompt = "admin> "
        print("Logged out successfully")
    
    def check_auth(self):
        
        if not self.current_user or not self.token:
            print("Not logged in. Please login first.")
            return False
            
        success, result = self.auth.verify_session(self.token)
        if not success:
            print(f"Session error: {result}")
            self.token = None
            self.current_user = None
            self.prompt = "admin> "
            return False
            
        return True
    
    def do_status(self, arg):
        
        if not self.check_auth():
            return
            
        from utils.vote_storage import count_votes
        
        status = self.election.get_election_status()
        # Update votes_cast with the file-based count
        status['votes_cast'] = count_votes()
        
        print("\nElection Status:")
        print("-" * 50)
        for key, value in status.items():
            print(f"{key}: {value}")

    
    def do_set_title(self, arg):
        
        if not self.check_auth():
            return
            
        if not arg:
            print("Please provide a title")
            return
            
        success = self.election.set_title(arg)
        if success:
            print(f"Election title set to: {arg}")
        else:
            print("Failed to set election title")
    
    def do_set_description(self, arg):
        
        if not self.check_auth():
            return
            
        if not arg:
            print("Please provide a description")
            return
            
        success = self.election.set_description(arg)
        if success:
            print(f"Election description set to: {arg}")
        else:
            print("Failed to set election description")
    
    def do_change_state(self, arg):
       
        if not self.check_auth():
            return
            
        if not arg:
            print(f"Current state: {self.election.get_state()}")
            print(f"Available states: {', '.join(self.election.STATES)}")
            return
            
        success, message = self.election.change_state(arg.upper())
        print(message)
    
    def do_list_candidates(self, arg):
        
        if not self.check_auth():
            return
            
        candidates = self.candidates.list_candidates()
        if not candidates:
            print("No candidates registered")
            return
            
        print("\nCandidates:")
        print("-" * 50)
        for candidate in candidates:
            print(f"ID: {candidate['id']}, Name: {candidate['name']}")
            if "info" in candidate and candidate["info"].get("party"):
                print(f"  Party: {candidate['info']['party']}")
            print()
    
    def do_add_candidate(self, arg):
        
        if not self.check_auth():
            return
            
        name = input("Candidate name: ")
        party = input("Party (optional): ")
        bio = input("Bio (optional): ")
        
        success, message = self.candidates.add_candidate(name, party, bio)
        print(message)
    
    def do_remove_candidate(self, arg):
        
        if not self.check_auth():
            return
            
        try:
            candidate_id = int(arg) if arg else int(input("Candidate ID: "))
            success, message = self.candidates.remove_candidate(candidate_id)
            print(message)
        except ValueError:
            print("Invalid candidate ID")
    
    def do_generate_report(self, arg):
        
        if not self.check_auth():
            return
            
        print("\nAvailable Reports:")
        print("1. Voter report")
        print("2. Election results")
        print("3. Blockchain report")
        
        choice = input("Select report type (1-3): ")
        
        if choice == "1":
            success, message = self.reports.generate_voter_report()
        elif choice == "2":
            success, message = self.reports.generate_result_report()
        elif choice == "3":
            success, message = self.reports.generate_blockchain_report()
        else:
            print("Invalid choice")
            return
            
        print(message)
    
    def do_tally_votes(self, arg):
       
        if not self.check_auth():
            return
            
        if self.election.get_state() not in ["TALLYING", "CLOSED"]:
            print("Cannot tally votes until election is in TALLYING or CLOSED state")
            print(f"Current state: {self.election.get_state()}")
            change = input("Change to TALLYING state? (y/n): ")
            if change.lower() == 'y':
                success, message = self.election.change_state("TALLYING")
                print(message)
            else:
                return
                
        success, results = self.election.get_results()
        if not success:
            print("Error tallying votes")
            return
            
        print("\nElection Results:")
        print("-" * 50)
        
        for candidate in sorted(results, key=lambda x: x["votes"], reverse=True):
            name = candidate["name"]
            votes = candidate["votes"]
            percentage = (votes / sum(c["votes"] for c in results)) * 100 if results else 0
            
            print(f"{name}: {votes} votes ({percentage:.1f}%)")
    
    def do_register_voter(self, arg):
        
        if not self.check_auth():
            return
            
        if self.election.get_state() not in ["SETUP", "REGISTRATION"]:
            print("Voter registration is only allowed during SETUP or REGISTRATION phases")
            return
            
        voter_address = input("Enter voter public key: ")
        if not voter_address:
            print("Voter public key is required")
            return
            
        success, auth_factors = self.blockchain.register_voter(voter_address)
        if success:
            # Use the simple OTP storage instead of saving the whole blockchain
            from utils.otp_storage import save_otp
            save_otp(voter_address, auth_factors['otp'])
            
            print(f"Voter registered successfully")
            print(f"OTP code for voter: {auth_factors['otp']}")
        else:
            print(f"Error registering voter: {auth_factors}")

    
    def do_exit(self, arg):
       
        if self.current_user:
            self.auth.logout(self.token)
        print("Exiting admin interface...")
        return True
        
    def do_quit(self, arg):
        
        return self.do_exit(arg)

def run_admin_interface(blockchain):
   
    interface = AdminInterface(blockchain)
    interface.cmdloop()
