#!/usr/bin/perl -w
# this script catch each url from your irssi and sends it to collectr.
# it's highly inspired of yacoob urlinfo script available at 'http://iceteajunkie.wordpress.com'

use strict;

use LWP::UserAgent;
use POSIX;
use URI::Escape;


use Irssi;
our ($VERSION, %IRSSI);

$VERSION = "0.1";
%IRSSI=(
    author  => 'dzen',
    contact => 'dzentoo@gmail.com',
    name    => 'Sends url to collectr',
    license => 'BSD',
    modules => 'LWP::UserAgent POSIX',
    url     => 'http://links.litchis.org'
);

our ($browser);

# handler for incoming messages
sub look_for_urls {
  my ($server, $msg, $nick, $address, $target) = @_;
  my $urlre = qr#((?:https?://[^\s<>"]+|www\.[-a-z0-9.]+)[^\s.,;<">\):])#;

  # are there any urls to handle?
  my @all_urls = ($msg =~ /$urlre/g);

  my ($channel,$text,$msgline,$msgnick,$curchan,$curserv);
  ($channel, $text) = $msg =~ /^(\S*)\s:(.*)/;
  $msgnick = $server->{nick};
  $curchan = $channel;
  # exit if there were no urls
  return if (scalar(@all_urls) == 0);

  # if there was more than one url on the line, flip the switch to output
  # information in multiple lines
  my $annotate = 0;
  if (scalar(@all_urls) > 1) {
    $annotate = 1;
  }

  # handle private msgs
  unless (defined($target)) {
    $target = $nick;
  }

  # loop through URLs
  while (my $url = shift @all_urls) {
    # setup pipe for parent<->child communication
    my ($rh, $wh);
    pipe ($rh, $wh);

    # FIXME: limit number of forks here, to avoid DoS

    my $base_url = Irssi::settings_get_str('collectr_url');
    my $collectr_username = Irssi::settings_get_str('collectr_username');
    my $collectr_token = Irssi::settings_get_str('collectr_token');
    my $final_target = $target;
    $final_target =~ s/#//g;
    $url = uri_escape($url);
    my $final_url = "$base_url/$collectr_username/?url=$url&from=".$nick."@".$final_target."&source=irc&token=".$collectr_token;
    #my $i = handle_url($final_url);
    my $child = fork();
    unless (defined $child) {
      print "Argh, fork failed. No info about $url will be given.";
    }

    # main process - call wait on kid, setup watcher for incoming data over pipe
    if ($child >0) {
      close ($wh);
      Irssi::pidwait_add($child);
      my $pipetag;
      my $args = [$rh, \$pipetag, $url, $server, $target, $annotate];
      $pipetag  = Irssi::input_add(fileno($rh), INPUT_READ, 'read_info', $args);
    } 

    # kid - get description for url, throw it down the pipe, exit
    if ($child == 0) {
      my $i = handle_url($final_url);
      binmode ($wh, ":utf8");
      print ($wh $i);
      close ($wh);
      POSIX::_exit(1);
    }
  }

}

# get response from forked process, display it
sub read_info {
  my $args = shift @_;
  my ($rh, $pipetag, $url, $server, $target, $annotate) = @$args;

  my $d;
  while (<$rh>) {
    $d .= $_;
  }
  close ($rh);
  Irssi::input_remove($$pipetag);

  my $output = "::: $d";
  if ($annotate) {
    $output .= " - <$url>";
  }
  
}

# fetch webpage, parse it, try to get <title>
sub handle_url {    
  my ($url) = @_;

  my $info;
  my $response = $browser->get($url);
  if (!$response->is_success) {
    $info = "Error adding $url";
    print $response->status_line;
  } else {
    $info = undef;
  }

  return $info;
}

# create browser
$browser = LWP::UserAgent->new();
$browser->max_size(1000);
$browser->agent('Mozilla/5.0 collectr irssi');
$browser->env_proxy;
$browser->timeout(3);

# define settings
Irssi::settings_add_str('collectr', 'collectr_username', "blank");
Irssi::settings_add_str('collectr', 'collectr_token', "blank");
Irssi::settings_add_str('collectr', 'collectr_url', "http://links.litchis.org/collector/bookmark/secret");

# hook on irssi signals
Irssi::signal_add('message public', 'look_for_urls');
