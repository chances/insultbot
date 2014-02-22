# InsultBot
########################################################
# Written by Chance Snow - enigma <chances@cat.pdx.edu>
# Licensed under the MIT License
# See LICENSE file for more info
########################################################

require 'cinch'
require 'cinch/plugins/identify'
require 'date'
require 'open-uri'
require 'nokogiri'

@debug = false
if ARGV.length > 0
  if ARGV.include?('--debug')
    @debug = true
    puts 'DEBUG MODE'
  end
end

insultbot = Cinch::Bot.new do
  configure do |c|
    c.server = 'iss.cat.pdx.edu'
    c.port = 6697
    c.ssl.use = true
    c.nick = 'insultbot'
    c.realname = 'Enigma\'s InsultBot'
    #TODO: Re-add channel config file
    if ARGV.include?('--debug')
      c.channels = ['#insultbot']
    else
      c.channels = ['#insultbot', '#gnarwals catsonly', '#swearingparlour']
    end
    c.messages_per_second = 20
    c.plugins.plugins = [Cinch::Plugins::Identify]
    c.plugins.options[Cinch::Plugins::Identify] = {
      :password => 'insultbotiscool',
      :type => :nickserv
    }
  end
  
  helpers do
    @help = 'See http://web.cecs.pdx.edu/~chances/insults/help'
    @thanks = ['Thanks!', 'Much obliged.', 'Cheers!', 'Thank you.', 'Cool karma.']
    @minus = ['What gives?', 'That was uncalled for!', 'Not cool.', 'Was it something I said?']
    @services = [
      'http://www.randominsults.net/',
      'http://web.cecs.pdx.edu/~chances/insults/insult/random?format=text'
    ]
    
    def help(user)
      for line in @help.split('\n')
        user.msg line
      end
    end
    
    def insult(to)
      #Get an insult
      service = @services.sample
      insult = nil
      case service
      when @services[0] #Random Insults.net
        page = Nokogiri::HTML(open(service))
        insult = page.css('i').first.text
      #when @services[1] #InsultBot Suggestions
      #  open(service) do |file|
      #    insult = file.read
      #  end
      else
        page = Nokogiri::HTML(open(@services[0]))
        insult = page.css('i').first.text
      end
      
      #Insult the user
      if not insult == nil
        info "Insulting #{to}"
        if insult.include? '<NICK>'
          insult.gsub('<NICK>', to)
        else
          "Hey #{to}! #{insult}"
        end
      else
        info "ERROR: Failed to retrieve an insult"
      end
    end
  end
  
  on :connect do |m|
    info '------------------------------------------------'
    for channel in m.bot.config.channels
      info "Joining #{channel.split(' ')[0]}"
    end
    info '------------------------------------------------'
  end
  
  on :channel, /^!help insultbot$/ do |m|
    m.reply(@help)
  end
  on :channel, /^!insultbot (\w+)\s*(.*)/ do |m, command, args|
    from = m.user.nick
    case command
    when /help/
      m.reply(@help)
    when /(greet|insult)/
      if args != m.bot.nick
        if args == 'me'
          m.reply insult(from)
        else
          m.reply insult(args)
        end
      else
        m.reply insult(from)
      end
    when /leave/
      if from == 'enigma'
        m.reply insult(from)
        info "Leaving #{m.channel}"
        m.bot.part(m.channel)
      end
    when /quit/
      if from == 'enigma'
        m.reply insult(from)
        info 'Quitting IRC'
        m.bot.quit('Quitting at the request of my master')
      end
    else
      m.reply "[Error] #{insult(from)}"
    end
  end
  on :channel, /^insult: (.+)/ do |m, who|
    if who == 'me'
      m.reply insult(m.user.nick)
    elsif who != m.bot.nick
      m.reply insult(who)
    else
      m.reply insult(m.user.nick)
    end
  end
  on :channel, /(insultbot|InsultBot)/ do |m|
    from = m.user.nick
    return if from == m.bot.nick
    unless m.message.match /^(!insultbot.*|!help insultbot|insult: .*|infoobot: .*)/
      if m.message.match /(insultbot|InsultBot)\+\+/
        m.reply "#{from}: #{@thanks.sample}"
      elsif m.message.match /(insultbot|InsultBot)--/
        m.reply "#{from}: #{@minus.sample}"
      else
        #TODO: Make some insults actions.
        if m.action?
          m.reply insult(from)
        else
          m.reply insult(from)
        end
      end
    end
  end
end

#Set log file
log_file = File.open(File.expand_path('~/.bots/insultbot.log'), 'a')
log_file.sync = true
insultbot.loggers << Cinch::Logger.new(log_file)
insultbot.loggers.level = :info
insultbot.loggers.first.level  = :info

log_file.puts '================================================'
log_file.puts DateTime.now.strftime('%a, %b %d, %Y - %I:%M:%S %p')
log_file.puts '------------------------------------------------'

if @debug
  log_file.puts 'DEBUG MODE'
  log_file.puts '------------------------------------------------'
end

insultbot.start
